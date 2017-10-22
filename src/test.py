#!/usr/bin/env python3

import unittest

from type_infer import TypeVar, ArrowType, Context, Int, Float, Bool, ConflictingTypeError


v1 = TypeVar('1')
v2 = TypeVar('2')
v3 = TypeVar('3')
v4 = TypeVar('4')
v5 = TypeVar('5')
v6 = TypeVar('6')


class TypeInferTest(unittest.TestCase):
    def test_simple_chain(self):
        pairs = [(v1, v2), (v3, v2), (v3, v4)]
        results, assumptions = Context().infer_types(pairs, {v4: Int})
        self.assertEqual(results, {v1: Int, v2: Int, v3: Int, v4: Int})
        self.assertEqual(assumptions, {})

    def test_simple_chain_duplicate(self):
        pairs = [(v1, v2), (v3, v2), (v3, v4)]
        results, assumptions = Context().infer_types(pairs, {v4: Int, v2: Int})
        self.assertEqual(results, {v1: Int, v2: Int, v3: Int, v4: Int})
        self.assertEqual(assumptions, {})

    def test_simple_chain_fail(self):
        pairs = [(v1, v2), (v3, v2), (v3, v4)]
        with self.assertRaises(ConflictingTypeError):
            Context().infer_types(pairs, {v4: Int, v1: Bool})

    def test_simple_var_resolution(self):
        pairs = [(v1, v2)]
        results, assumptions = Context().infer_types(pairs, {v1: Int, v2: TypeVar('a')})
        self.assertEqual(results, {v1: Int, v2: Int})
        self.assertEqual(assumptions, {TypeVar('a'): Int})

    def test_complex_var(self):
        pairs = [(v1, v2), (v3, v4)]
        a = TypeVar('a')
        results, assumptions = Context().infer_types(pairs, {v1: Int, v2: a, v3: a, v4: Int})
        self.assertEqual(results, {v1: Int, v2: Int, v3: Int, v4: Int})
        self.assertEqual(assumptions, {a: Int})

    def test_complex_fail(self):
        pairs = [(v1, v2), (v3, v4)]
        a = TypeVar('a')
        with self.assertRaises(ConflictingTypeError):
            Context().infer_types(pairs, {v1: Int, v2: a, v3: a, v4: Float})

    def test_nested_match(self):
        a = TypeVar('a')
        pairs = [(v1, v2), (v3, v4)]

        t1 = ArrowType(Int, Int)
        t2 = ArrowType(Int, a)
        known = {v1: t1, v2: t2, v3: a, v4: Int}

        result, assumptions = Context().infer_types(pairs, known)
        self.assertEqual(result, {v1: t1, v2: t1, v3: Int, v4: Int})
        self.assertEqual(assumptions, {a: Int})

    def test_nested_match_fail(self):
        a = TypeVar('a')
        pairs = [(v1, v2), (v3, v4)]

        t1 = ArrowType(Int, Int)
        t2 = ArrowType(Int, a)
        known = {v1: t1, v2: t2, v3: a, v4: Float}

        with self.assertRaises(ConflictingTypeError):
            Context().infer_types(pairs, known)

    def test_related_nested_match(self):
        a = TypeVar('a')
        b = TypeVar('b')
        pairs = [(v1, v2), (v3, v4)]

        t1 = ArrowType(Int, a)
        t2 = ArrowType(Int, b)
        t3 = ArrowType(Bool, Float)
        t4 = ArrowType(Bool, b)
        known = {v1: t1, v2: t2, v3: t3, v4: t4}

        result, assumptions = Context().infer_types(pairs, known)
        self.assertEqual(assumptions, {a: Float, b: Float})
        i2f = ArrowType(Int, Float)
        b2f = ArrowType(Bool, Float)
        self.assertEqual(result, {v1: i2f, v2: i2f, v3: b2f, v4: b2f})


    def test_complex_nested_match(self):
        a = TypeVar('a')
        b = TypeVar('b')
        c = TypeVar('c')

        pairs = [(v1, v2), (v3, v4), (v5, v6)]
        t1 = ArrowType(Int, a)
        t2 = ArrowType(Int, b)
        t3 = ArrowType(b, Int)
        t4 = c
        t5 = ArrowType(Bool, c)
        t6 = ArrowType(Bool, ArrowType(Int, Int))
        known = {v1: t1, v2: t2, v3: t3, v4: t4, v5: t5, v6: t6}

        result, assumptions = Context().infer_types(pairs, known)
        self.assertEqual(result, {
            v1: ArrowType(Int, Int),
            v2: ArrowType(Int, Int),
            v3: ArrowType(Int, Int),
            v4: ArrowType(Int, Int),
            v5: ArrowType(Bool, ArrowType(Int, Int)),
            v6: ArrowType(Bool, ArrowType(Int, Int)),
        })

    def test_arrow_assumption(self):
        a = TypeVar('a')
        b = TypeVar('b')
        pairs = [(v1, v2), (v3, v4)]
        known = {v1: a, v2: ArrowType(b, Int), v3: Bool, v4: b}

        result, assumptions = Context().infer_types(pairs, known)
        b2i = ArrowType(Bool, Int)
        self.assertEqual(result, {v1: b2i, v2: b2i, v3: Bool, v4: Bool})
        self.assertEqual(assumptions, {a: ArrowType(b, Int), b: Bool})
        # TODO: could multiple assumptions containing type vars ever result in
        # failing to unify two variables?

if __name__ == '__main__':
    unittest.main()
