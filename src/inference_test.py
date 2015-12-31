#!/usr/bin/env python3

import unittest

from expression import Application
from expression import If
from expression import Lambda
from expression import Let
from expression import Literal
from expression import TypedExpression
from expression import Variable
from infer import Rules, Registry, InferenceError, Result

class InferenceTest(unittest.TestCase):
    def setUp(self):
        self._rules = Rules()
        self._registry = Registry()

    def test_nonpolymorphic_variable(self):
        self._registry.push_new_scope({'foo': ('var_foo_1', False)})
        v = Variable('foo')
        v_id = v.add_to_rules(self._rules, self._registry)
        self.assertEqual(Result({}, {}), self._rules.infer())

    def test_polymorphic_variable(self):
        self._registry.push_new_scope({'foo': ('var_foo_1', True)})
        v = Variable('foo')
        v_id = v.add_to_rules(self._rules, self._registry)
        self.assertEqual(Result({}, {}), self._rules.infer())

    def test_literal(self):
        l = Literal('Int', 123)
        l_id = l.add_to_rules(self._rules, self._registry)
        self.assertEqual(Result({l_id: 'Int'}, {}), self._rules.infer())

    def test_typed_expression_mismatch(self):
        te = TypedExpression('String', Literal('Int', 123))
        te_id = te.add_to_rules(self._rules, self._registry)
        with self.assertRaises(InferenceError):
            self._rules.infer()

    def test_typed_expression_match(self):
        lit = Literal('Int', 123)
        te = TypedExpression('Int', lit)
        te_id = te.add_to_rules(self._rules, self._registry)
        lit_id = self._registry.get_id_for(lit)
        result = self._rules.infer()
        self.assertEqual('Int', result.get_type_by_id(te_id))
        self.assertEqual('Int', result.get_type_by_id(lit_id))

    def test_application(self):
        self._registry.push_new_scope({'times2': ('var_times2_1', True)})
        v = Variable('times2')
        l = Literal('Int', 123)
        a = Application(v, [l])
        a_id = a.add_to_rules(self._rules, self._registry)
        v_id = self._registry.get_id_for(v)
        l_id = self._registry.get_id_for(l)

        result = self._rules.infer()
        self.assertEqual('Int', result.get_type_by_id(l_id))
        self.assertEqual(None, result.get_type_by_id(a_id))

    def test_let(self):
        l = Literal('Int', 123)
        lt = Let([('x', l)], Variable('x'))
        lt_id = lt.add_to_rules(self._rules, self._registry)

        result = self._rules.infer()
        self.assertEqual('Int', result.get_type_by_id(lt_id))

    def test_multi_let(self):
        l = Literal('Int', 123)
        lt = Let([('x', Variable('y')), ('y', l)], Variable('x'))
        lt_id = lt.add_to_rules(self._rules, self._registry)
        l_id = self._registry.get_id_for(l)

        result = self._rules.infer()
        self.assertEqual('Int', result.get_type_by_id(lt_id))

    def test_lambda_exprssion(self):
        lm = Lambda(['x'], Variable('x'))
        lmid = lm.add_to_rules(self._rules, self._registry)

        result = self._rules.infer()
        self.assertEqual(
            ('Fn_1', 'var_x_2', 'var_x_2'),
            result.get_type_by_id(lmid)
        )

    def test_let_with_lambda(self):
        ''' ML code:
        let id = \\x -> x
        in id 'foo'
        '''
        lm = Lambda(['x'], Variable('x'))
        var_id = Variable('id')
        app = Application(var_id, [Literal('String', 'foo')])
        lt = Let([('id', lm)], app)
        lt_id = lt.add_to_rules(self._rules, self._registry)

        result = self._rules.infer()
        self.assertEqual('String', result.get_type_by_id(lt_id))

    def test_polymorphism(self):
        ''' ML code:
        let id = \\x -> x
        in (id id) 123
        '''
        lm = Lambda(['x'], Variable('x'))
        app1 = Application(Variable('id'), [Variable('id')])
        app2 = Application(app1, [Literal('Int', 123)])
        lt = Let([('id', lm)], app2)
        lt_id = lt.add_to_rules(self._rules, self._registry)

        result = self._rules.infer()
        self.assertEqual('Int', result.get_type_by_id(lt_id))

    def test_if_statement(self):
        test = Literal('Bool', True)
        if_case = Literal('Int', 123)
        else_case = Literal('Int', 456)
        if_block = If(test, if_case, else_case)

        if_id = if_block.add_to_rules(self._rules, self._registry)
        result = self._rules.infer()

        self.assertEqual('Int', result.get_type_by_id(if_id))

    def test_if_statement_requires_branches_to_equal(self):
        test = Literal('Bool', True)
        if_case = Literal('Int', 123)
        else_case = Literal('Float', 456)
        if_block = If(test, if_case, else_case)

        if_id = if_block.add_to_rules(self._rules, self._registry)
        with self.assertRaises(InferenceError):
            self._rules.infer()

    def test_if_statement_requires_test_to_be_boolean(self):
        test = Literal('String', 'not a boolean')
        if_case = Literal('Int', 123)
        else_case = Literal('Int', 456)
        if_block = If(test, if_case, else_case)

        if_id = if_block.add_to_rules(self._rules, self._registry)
        with self.assertRaises(InferenceError):
            self._rules.infer()

    def test_mutual_recursion(self):
        '''
        Equivalent ML:

        let-rec f = if True then 123 else g
                g = f
        in f
        '''
        test = Literal('Bool', True)
        if_case = Literal('Int', 123)
        else_case = Application(Variable('g'), [])
        if_block = If(test, if_case, else_case)
        f_func = Lambda([], if_block)

        g_body = Application(Variable('f'), [])
        g_func = Lambda([], g_body)

        let_body = Variable('f')
        let_expr = Let([('f', f_func), ('g', g_func)], let_body)

        let_id = let_expr.add_to_rules(self._rules, self._registry)
        result = self._rules.infer()
        self.assertEqual(('Fn_0', 'Int'), result.get_full_type_by_id(let_id))

    def test_generic_mutual_recursion(self):
        '''
        Equivalent ML:

        let-rec f x = if True then x else g x
                g y = f y
        in g
        '''
        test = Literal('Bool', True)
        if_case = Variable('x')
        else_case = Application(Variable('g'), [Variable('x')])
        if_block = If(test, if_case, else_case)
        f_func = Lambda(['x'], if_block)

        g_body = Application(Variable('f'), [Variable('y')])
        g_func = Lambda(['y'], g_body)

        let_body = Variable('f')
        let_expr = Let([('f', f_func), ('g', g_func)], let_body)

        let_id = let_expr.add_to_rules(self._rules, self._registry)
        result = self._rules.infer()
        self.assertEqual(('Fn_1', 'a0', 'a0'), result.get_full_type_by_id(let_id))


'''
TODO: test this:

data CrazyList a = CL a (CrazyList [a]) | End

f :: CrazyList a -> Int
f End         = 0
f (CL x rest) = g x rest

g :: a -> CrazyList [a] -> Int
g x rest = 1 + (f rest)

in this system
'''

if __name__ == '__main__':
    unittest.main()
