#!/usr/bin/env python3

import unittest

from graph import *

class GraphTest(unittest.TestCase):
    def test_foo(self):
        expected = Graph.from_edges([
            (1, 0), (2, 1), (4, 1), (5, 1), (3, 2), (6, 2), (2, 3),
            (7, 3), (0, 4), (5, 4), (6, 5), (5, 6), (3, 7), (6, 7),
        ])

        self.assertEqual(expected, multi_component_graph().invert())

    def test_walk_dfs(self):
        g = multi_component_graph()
        expected_vertices = sorted(g.get_vertices())

        actual_vertices = []

        def f(v):
            actual_vertices.append(v)
        g.dfs(f)
        actual_vertices.sort()

        self.assertEqual(expected_vertices, actual_vertices)

    def test_finds_strongly_connected_components(self):
        result = multi_component_graph().strongly_connected_components()
        expected = [{5, 6}, {2, 3, 7}, {0, 1, 4}]
        self.assertEqual(expected, result)

def multi_component_graph():
    return Graph.from_edges([
        (0, 1), (1, 2), (1, 4), (1, 5), (2, 3), (2, 6), (3, 2),
        (3, 7), (4, 0), (4, 5), (5, 6), (6, 5), (7, 3), (7, 6),
    ])

if __name__ == '__main__':
    unittest.main()
