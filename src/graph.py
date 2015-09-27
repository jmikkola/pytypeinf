#!/usr/bin/env python3

import collections
import itertools

class Graph:
    def __init__(self, vertices, edges):
        self._vertices = vertices
        self._edges = edges

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other._vertices == self._vertices and other._edges == self._edges

    @classmethod
    def new(cls):
        return cls(vertices=set(), edges=collections.defaultdict(set))

    @classmethod
    def with_vertices(cls, vertices):
        return cls(vertices=set(vertices), edges=collections.defaultdict(set))

    @classmethod
    def from_edges(cls, edges):
        g = Graph.new()
        g.add_edges(edges)
        return g

    def __len__(self):
        return len(self._vertices)

    def add_edge(self, start, end):
        self._vertices.add(start)
        self._vertices.add(end)
        self._edges[start].add(end)

    def add_edges(self, edges):
        for (start, end) in edges:
            self.add_edge(start, end)

    def invert(self):
        inverted = self.with_vertices(self._vertices)

        for start, ends in self._edges.items():
            for end in ends:
                inverted.add_edge(end, start)

        return inverted

    def dfs(self, f):
        seen = set()
        for v in self._vertices:
            self._walk_dfs(v, seen, f)

    def _walk_dfs(v, seen, f):
        if v in seen:
            return

        seen.insert(v)
        f(v)

        for child in self._edges.get(v, []):
            self._walk_dfs(child, seen, f)

    def strongly_connected_components(self):
        index = itertools.count(0)
        indexes = {}
        lowlinks = {}
        in_stack = set()
        stack = []
        components = []

        for v in self._vertices:
            if v in indexes:
                continue
            self._strong_conn(
                v, index, indexes, lowlinks, in_stack, stack, components
            )

        return components

    def _strong_conn(self, root, index, indexes, lowlinks, in_stack, stack, components):
        stack.push(root)
        in_stack.add(root)

        node_index = next(index)
        lowlink = node_index
        indexes[root] = node_index
        lowlinks[root] = lowlink

        for child in self._edges.get(root, []):
            if child not in indexes:
                child_lowlink = self._strong_conn(
                    child, index, indexes, lowlinks, in_stack, stack, components
                )
                lowlink = min(lowlink, child_lowlink)
            elif child in in_stack:
                lowlink = min(lowlink, lowlinks[child])

        lowlinks[root] = lowlink

        if node_index == lowlink:
            component = set()
            while stack:
                v = stack.pop()
                is_stack.remove(v)

                component.insert(v)
                if v == root:
                    break

            components.push(component)

        return lowlink
