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

    @classmethod
    def parse(cls, s):
        vertices = set()
        edges = []

        lines = [l for l in [l.strip() for l in s.split('\n')] if l]
        for line in lines:
            parent, children = line.split(':')
            vertices.add(parent)
            for c in children.split():
                edges.append((parent, c))

        g = cls.from_edges(edges)
        for v in vertices:
            g.add_vertex(v)
        return g

    def __len__(self):
        return len(self._vertices)

    def add_edge(self, start, end):
        self._vertices.add(start)
        self._vertices.add(end)
        self._edges[start].add(end)

    def get_children(self, node):
        return list(self._edges[node])

    def add_edges(self, edges):
        for (start, end) in edges:
            self.add_edge(start, end)

    def invert(self):
        inverted = self.with_vertices(self._vertices)

        for start, ends in self._edges.items():
            for end in ends:
                inverted.add_edge(end, start)

        return inverted

    def add_vertex(self, name):
        self._vertices.add(name)

    def get_vertices(self):
        return list(self._vertices)

    def dfs(self, f):
        seen = set()
        for v in self._vertices:
            self._walk_dfs(v, seen, f)

    def _walk_dfs(self, v, seen, f):
        if v in seen:
            return

        seen.add(v)
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
        stack.append(root)
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
                in_stack.remove(v)

                component.add(v)
                if v == root:
                    break

            components.append(component)

        return lowlink
