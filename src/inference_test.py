#!/usr/bin/env python3

import unittest

from expression import Application
from expression import Lambda
from expression import Let
from expression import Literal
from expression import TypedExpression
from expression import Variable
from infer import Rules, Registry, InferenceError

class InferenceTest(unittest.TestCase):
    def setUp(self):
        self._rules = Rules()
        self._registry = Registry()

    def test_variable(self):
        v = Variable('foo')
        v_id = v.add_to_rules(self._rules, self._registry)
        self.assertEqual(({}, {}), self._rules.infer())

    def test_literal(self):
        l = Literal('Int', 123)
        l_id = l.add_to_rules(self._rules, self._registry)
        self.assertEqual(({l_id: 'Int'}, {}), self._rules.infer())

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
        # TODO: this test is relying on accidental order of processing
        self.assertEqual(({te_id: 'Int'}, {lit_id: te_id}), self._rules.infer())

    def test_application(self):
        v = Variable('times2')
        l = Literal('Int', 123)
        a = Application(v, [l])
        a_id = a.add_to_rules(self._rules, self._registry)
        v_id = self._registry.get_id_for(v)
        l_id = self._registry.get_id_for(l)

        expected_types = {l_id: 'Int', v_id: ('Fn_1', l_id, a_id)}
        self.assertEqual((expected_types, {}), self._rules.infer())

    def test_let(self):
        l = Literal('Int', 123)
        lt = Let(['x', 'y'], [Variable('y'), l], Variable('x'))
        lt_id = lt.add_to_rules(self._rules, self._registry)
        l_id = self._registry.get_id_for(l)

        expected_types = {l_id: 'Int'}
        expected_subs = {lt_id: l_id, 'var_x': l_id, 'var_y': l_id}
        self.assertEqual((expected_types, expected_subs), self._rules.infer())

    def test_lambda_exprssion(self):
        lm = Lambda(['x'], Variable('x'))
        lmid = lm.add_to_rules(self._rules, self._registry)

        expected_types = {lmid: ('Fn_1', 'var_x', 'var_x')}
        expected_subs = {}
        self.assertEqual((expected_types, expected_subs), self._rules.infer())

    def test_let_with_lambda(self):
        ''' ML code:
        let id = \\x -> x
        in id 123
        '''
        lm = Lambda(['x'], Variable('x'))
        var_id = Variable('id')
        app = Application(var_id, [Literal('Int', 123)])
        lt = Let(['id'], [lm], app)

        lt_id = lt.add_to_rules(self._rules, self._registry)
        app_id = self._registry.get_id_for(app)

        '''
        expected_types = {
        }
        expected_subs = {
        }
        self.assertEqual((expected_types, expected_subs), self._rules.infer())
        '''

if __name__ == '__main__':
    unittest.main()
