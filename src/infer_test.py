#!/usr/bin/env python3

import unittest

from infer import Rules, Registry, InferenceError

class InferTest(unittest.TestCase):
    def test_passthrough(self):
        self.assertEqual(({}, {}), Rules().infer())
        self.assertEqual(({1: 'Int'}, {}), Rules().specify(1, 'Int').infer())

    def test_applies_substitution(self):
        self.assertEqual(
            ({1: 'Int'}, {2: 1}),
            Rules().specify(1, 'Int').equal(1, 2).infer()
        )
        self.assertEqual(
            ({1: 'Int'}, {2: 1}),
            Rules().specify(1, 'Int').specify(2, 'Int').equal(1, 2).infer()
        )

    def test_catches_incompatible_sub(self):
        rules = Rules().specify(1, 'Int').specify(2, 'Float').equal(1, 2)
        with self.assertRaises(InferenceError):
            rules.infer()

    def test_complicated_subs_work(self):
        rules = (
            Rules().specify(1, 'Int').equal(3, 4).equal(1, 5).equal(1, 2)
            .equal(5, 2).equal(4, 5)
        )
        self.assertEqual(({1: 'Int'}, {2: 1, 3: 1, 4: 1, 5: 1}), rules.infer())

    def test_rejects_invalid_generic_relations(self):
        rules = (
            Rules().specify(1, 'Int').specify(3, 'Float')
            .equal(1, 2).instance_of(2, 3)
        )
        with self.assertRaises(InferenceError):
            rules.infer()

    def test_applies_generic_relations(self):
        types, _ = Rules().specify(1, 'Int').instance_of(2, 1).infer()
        self.assertEqual(types.get(2), 'Int')

    def test_ignores_reverse_relation(self):
        types, _ = Rules().specify(1, 'Int').instance_of(1, 2).infer()
        self.assertEqual(types.get(2), None)

    def test_accepts_circular_generic_relations(self):
        types, _ = (
            Rules().specify(1, 'Int').instance_of(1, 2).instance_of(2, 1)
            .infer()
        )
        self.assertEqual(types.get(2), 'Int')

    def test_applies_recurisve_equality(self):
        rules = (
            Rules().specify(1, ('Pair', 11, 12)).specify(2, ('Pair', 21, 22))
            .specify(11, 'Int').specify(22, 'String')
            .equal(1, 2)
        )
        types, subs = rules.infer()
        self.assertEqual({1: ('Pair', 11, 22), 11: 'Int', 22: 'String'}, types)
        self.assertEqual({2: 1, 21: 11, 12: 22}, subs)

    def test_applies_generics_recursively(self):
        rules = (
            Rules().specify(1, ('Pair', 11, 12)).specify(2, ('Pair', 21, 22))
            .specify(11, 'Int').specify(22, 'String')
            .instance_of(1, 2)
        )
        expected_types = {
            1: ('Pair', 11, 12),
            2: ('Pair', 21, 22),
            11: 'Int',
            12: 'String',
            22: 'String',
        }
        self.assertEqual((expected_types, {}), rules.infer())

    def test_allows_multiple_generic_instantiations(self):
        rules = (
            Rules().specify(1, ('List', 11))
            .specify(2, ('List', 21)).specify(3, ('List', 31))
            .specify(21, 'Int').specify(31, 'String')
            .instance_of(2, 1).instance_of(3, 1)
        )
        expected_types = {
            1: ('List', 11),
            2: ('List', 21),
            3: ('List', 31),
            21: 'Int',
            31: 'String',
        }
        self.assertEqual((expected_types, {}), rules.infer())

    def test_applies_generics_for_multiple_levels(self):
        rules = (
            Rules().specify(1, ('List', 11)).specify(11, 'Int')
            .instance_of(2, 1).instance_of(3, 1)
        )
        expected_types = {
            1: ('List', 11),
            2: ('List', 11),
            3: ('List', 11),
            11: 'Int',
        }
        self.assertEqual((expected_types, {}), rules.infer())

    def test_catches_generic_errors_with_separation(self):
        rules = (
            Rules().specify(1, ('List', 11)).specify(11, 'Int')
            .specify(3, ('List', 31)).specify(31, 'String')
            .instance_of(2, 1).instance_of(3, 1)
        )
        with self.assertRaises(InferenceError):
            rules.infer()

    def test_generates_new_ids(self):
        registry = Registry()
        self.assertEqual([1, 2, 3, 4],
                         [registry.generate_new_id() for _ in range(4)])

    def test_catches_duplicate_use_of_ids(self):
        registry = Registry()
        registry.register_for_id(1, 'x')
        with self.assertRaises(Exception):
            registry.register_for_id(1, 'x')

    def test_add_and_get_from_registry(self):
        registry = Registry()
        id1 = registry.add_to_registry('x')
        id2 = registry.add_to_registry('y')
        self.assertEqual('x', registry.get_registered()[id1])
        self.assertEqual('y', registry.get_registered()[id2])

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
