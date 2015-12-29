#!/usr/bin/env python3

import unittest

from expression import TypedExpression
from expression import Variable
from expression import Literal
from expression import Application
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
        self.assertTrue(te_id > 0)
        self.assertTrue(l_id > 0)
        self.assertNotEqual(l_id, te_id)
        self.assertSetEqual(
            set([(te_id, 'Num'), (l_id, 'Int')]),
            set(self._rules.specify_calls)
        )

if __name__ == '__main__':
    unittest.main()