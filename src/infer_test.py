#!/usr/bin/env python3

import unittest

from infer import Rules, InferenceError

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

if __name__ == '__main__':
    unittest.main()
