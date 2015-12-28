#!/usr/bin/env python3

import unittest

from graph import Graph

test_graph = Graph.parse('''
a: b
b: e f c
c: g d
d: c h
e: a f
f: g
g: f
h: g d
''')

class GraphTest(unittest.TestCase):
    def test_parsing(self):
        self.assertEqual(set('a b c d e f g h'.split()),
                         set(test_graph.get_vertices()))

    def test_strongly_connected_components(self):
        scc = test_graph.strongly_connected_components()
        expected = [{'g', 'f'}, {'d', 'c', 'h'}, {'e', 'b', 'a'}]
        self.assertEqual(expected, scc)

if __name__ == '__main__':
    unittest.main()
