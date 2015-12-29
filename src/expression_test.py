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

    def specify(self, *args):
        self.specify_calls.append(args)

    def equal(self, *args):
        self.equal_calls.append(args)

class ExpressionTest(unittest.TestCase):
    def setUp(self):
        self._rules = TestingRules()
        self._registry = Registry()

    def test_variable(self):
        v = Variable('foo')
        self.assertEqual('var_foo', v.add_to_rules(self._rules, self._registry))

    def test_literal(self):
        l = Literal('Int', 123)
        l_id = l.add_to_rules(self._rules, self._registry)
        self.assertTrue(l_id > 0)
        self.assertEqual([(l_id, 'Int')], self._rules.specify_calls)

    def test_typed_expression(self):
        l = Literal('Int', 123)
        te = TypedExpression('Num', l)
        te_id = te.add_to_rules(self._rules, self._registry)
        l_id = self._registry.get_id_for(l)
        self.assertNotEqual(l_id, te_id)
        self.assertSetEqual(
            set([(te_id, 'Num'), (l_id, 'Int')]),
            set(self._rules.specify_calls)
        )

    def test_application(self):
        v = Variable('times2')
        l = Literal('Int', 123)
        a = Application(v, [l])
        a_id = a.add_to_rules(self._rules, self._registry)
        v_id = self._registry.get_id_for(v)
        l_id = self._registry.get_id_for(l)

        self.assertIn((a_id, ('Fn_1', v_id, l_id)), self._rules.specify_calls)

    def test_let(self):
        lt = Let(
            ['x', 'y'], [Variable('y'), Literal('Int', 123)],
            Variable('x')
        )
        ltid = lt.add_to_rules(self._rules, self._registry)
        # TODO

    def test_lambda_exprssion(self):
        lm = Lambda(['x'], Variable('x'))
        lmid = lm.add_to_rules(self._rules, self._registry)
        # TODO

    def test_let_with_lambda(self):
        pass # TODO

if __name__ == '__main__':
    unittest.main()
