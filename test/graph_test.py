#!/usr/bin/env python3

import unittest

from graph import *

class GraphTest(unittest.TestCase):
    def test_foo(self):
        g = multi_component_graph()

def multi_component_graph():
    return Graph.from_edges([
        (0, 1), (1, 2), (1, 4), (1, 5), (2, 3), (2, 6), (3, 2),
        (3, 7), (4, 0), (4, 5), (5, 6), (6, 5), (7, 3), (7, 6),
    ])
    
if __name__ == '__main__':
    unittest.main()
