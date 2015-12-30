#!/usr/bin/env python3

import unittest

from expression import Application
from expression import Lambda
from expression import Let
from expression import Literal
from expression import TypedExpression
from expression import Variable
from infer import Registry

class TestingRules:
    def __init__(self):
        self.specify_calls = []
        self.equal_calls = []
        self.instance_of_calls = []

    def specify(self, *args):
        self.specify_calls.append(args)

    def equal(self, *args):
        self.equal_calls.append(args)

    def instance_of(self, *args):
        self.instance_of_calls.append(args)

class ExpressionTest(unittest.TestCase):
    def setUp(self):
        self._rules = TestingRules()
        self._registry = Registry()

    def test_variable_repr(self):
        self.assertEqual('Variable(foo)', repr(Variable('foo')))

    def test_variable(self):
        scoped_id = 'var_foo_1'
        self._registry.push_new_scope({'foo': (scoped_id, False)})
        v = Variable('foo')
        v_id = v.add_to_rules(self._rules, self._registry)
        self.assertEqual(v_id, scoped_id)
        self.assertEqual([], self._rules.instance_of_calls)

    def test_polymorphic_variable(self):
        scoped_id = 'var_foo_1'
        self._registry.push_new_scope({'foo': (scoped_id, True)})
        v = Variable('foo')
        v_id = v.add_to_rules(self._rules, self._registry)
        self.assertIn((v_id, scoped_id), self._rules.instance_of_calls)

    def test_literal_repr(self):
        self.assertEqual('Literal(Int, 123)', repr(Literal('Int', 123)))

    def test_literal(self):
        l = Literal('Int', 123)
        l_id = l.add_to_rules(self._rules, self._registry)
        self.assertTrue(l_id > 0)
        self.assertEqual([(l_id, 'Int')], self._rules.specify_calls)

    def test_typed_expression(self):
        l = Literal('Int', 123)
        te = TypedExpression('Num', l)
        self.assertEqual('TypedExpression(Num, Literal(Int, 123))', repr(te))
        te_id = te.add_to_rules(self._rules, self._registry)
        l_id = self._registry.get_id_for(l)
        self.assertNotEqual(l_id, te_id)
        self.assertSetEqual(
            set([(te_id, 'Num'), (l_id, 'Int')]),
            set(self._rules.specify_calls)
        )

    def test_application(self):
        scoped_id = 'var_times2_1'
        self._registry.push_new_scope({'times2': (scoped_id, True)})
        v = Variable('times2')
        l = Literal('Int', 123)
        a = Application(v, [l])
        a_id = a.add_to_rules(self._rules, self._registry)
        v_id = self._registry.get_id_for(v)
        l_id = self._registry.get_id_for(l)

        self.assertIn((v_id, scoped_id), self._rules.instance_of_calls)
        self.assertIn((v_id, ('Fn_1', l_id, a_id)), self._rules.specify_calls)

    def test_simple_let(self):
        l1 = Literal('Int', 123)
        l2 = Literal('Int', 456)
        lt = Let([('x', l1)], l2)
        lt_id = lt.add_to_rules(self._rules, self._registry)
        l1_id = self._registry.get_id_for(l1)
        l2_id = self._registry.get_id_for(l2)
        # TODO: the test is dependent on order for the name of var_x_1
        self.assertIn(('var_x_2', l1_id), self._rules.equal_calls)
        self.assertIn((lt_id, l2_id), self._rules.equal_calls)
        self.assertEqual([], self._rules.instance_of_calls)
        self.assertIn((l1_id, 'Int'), self._rules.specify_calls)
        self.assertIn((l2_id, 'Int'), self._rules.specify_calls)

    '''
    def test_let(self):
        l = Literal('Int', 123)
        lt = Let([('x', Variable('y')), ('y', l)], Variable('x'))
        ltid = lt.add_to_rules(self._rules, self._registry)
        l_id = self._registry.get_id_for(l)
        self.assertIn(('var_x', 'var_y'), self._rules.equal_calls)
        self.assertIn(('var_y', l_id), self._rules.equal_calls)
        self.assertIn((ltid, 'var_x'), self._rules.equal_calls)
    '''

    def test_simple_lambda_expression(self):
        lit = Literal('Int', 123)
        lm = Lambda(['x'], lit) # The `x` argument is unused
        lm_id = lm.add_to_rules(self._rules, self._registry)
        lit_id = self._registry.get_id_for(lit)
        # TODO: test is dependant on order for the name of var_x_2
        self.assertIn(
            (1, ('Fn_1', 'var_x_2', lit_id)),
            self._rules.specify_calls
        )
        self.assertIn((lit_id, 'Int'), self._rules.specify_calls)

    '''
    def test_lambda_exprssion(self):
        lm = Lambda(['x'], Variable('x'))
        lmid = lm.add_to_rules(self._rules, self._registry)
        self.assertEqual(
            [(1, ('Fn_1', 'var_x', 'var_x'))],
             self._rules.specify_calls
         )
    '''

    def test_let_with_lambda(self):
        lm = Lambda(['x'], Variable('x'))
        var_id = Variable('id')
        app = Application(var_id, [Literal('Int', 123)])
        lt = Let([('id', lm)], app)

        lt_id = lt.add_to_rules(self._rules, self._registry)
        app_id = self._registry.get_id_for(app)
        self.assertIn((lt_id, app_id), self._rules.equal_calls)

if __name__ == '__main__':
    unittest.main()
