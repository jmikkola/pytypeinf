#!/usr/bin/env python3

import unittest

from pytypeinf import *

class InferenceTest(unittest.TestCase):
    def test_is_more_general_than(self):
        cases = [
            (1, 1, True), # Both the same
            (21, 22, True), # Both undefined
            (3, 21, True), # Specific defined, general undefined
            (21, 3, False), # Specific undefined, general defined
            (3, 5, True), # Matching tcons
            (1, 4, True), # Matching recursive tcons
            (1, 3, False), # Mismatched tcons
            (7, 8, False), # Mismatched inner types
            (8, 1, True), # List[int] vs. List[a]
            (1, 8, False), # List[a] vs. List[int]
            (6, 2, True), # Pair[a,a] vs. Pair[b,c]
            (2, 6, False), # Pair[b,c] vs. Pair[a,a]
            (6, 9, True), # Pair[a,a] vs. Pair[b,b]
        ]

        resolutions = {
            1: list_type(10),
            2: pair_type(11, 12),
            3: int_type(),
            4: list_type(11),
            5: int_type(),
            6: pair_type(13, 13),
            7: list_type(2),
            8: list_type(3),
            9: pair_type(14, 14),
        }

        for (specific, general, expected) in cases:
            result = is_more_general_than(specific, general, resolutions)
            self.assertEqual(expected, result)

    def test_detects_type_merge_problems(self):
        with self.assertRaises(TypeInfError):
            merge_types(TypeConstructor('foo', []), TypeConstructor('bar', []))
        with self.assertRaises(TypeInfError):
            merge_types(TypeConstructor('foo', [1,2,3]), TypeConstructor('foo', [1]))

def list_type(inner):
    return TypeConstructor(name='List', components=[inner])

def int_type():
    return TypeConstructor(name='Int', components=[])

def pair_type(left, right):
    return TypeConstructor(name='Pair', components=[left, right])

if __name__ == '__main__':
    unittest.main()
