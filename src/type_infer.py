from collections import defaultdict


class InferError(Exception): pass


class NoTypeError(InferError):
    def __init__(self, point):
        self._point = point

    def __str__(self):
        return 'NoTypeError(' + str(self._point) + ')'


class ConflictingTypeError(InferError):
    def __init__(self, points, types):
        self._points = points
        self._types = types


class PrimType:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'PrimType(' + self._name + ')'

    def __repr__(self):
        return 'PrimType(' + repr(self._name) + ')'

    def __eq__(self, o):
        if isinstance(o, PrimType):
            return self._name == o._name
        return False

    def __hash__(self):
        return hash(str(self))


class ArrowType:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return 'ArrowType(' + str(self.left) + ', ' + str(self.right) + ')'

    def __repr__(self):
        return 'ArrowType(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def __eq__(self, o):
        if isinstance(o, ArrowType):
            return self.left == o.left and self.right == o.right
        return False

    def __hash__(self):
        return hash(str(self))


class TypeVar:
    def __init__(self, var):
        self._var = var

    def __str__(self):
        return 'TypeVar(' + self._var + ')'

    def __repr__(self):
        return 'TypeVar(' + repr(self._var) + ')'

    def __eq__(self, o):
        if isinstance(o, TypeVar):
            return self._var == o._var
        return False

    def __hash__(self):
        return hash(str(self))


class Context:
    def __init__(self):
        self._vars = {} # Not quite right, actually needs to be a graph


    def unify_types(self, types, related_points):
        t = types[0]
        for t2 in types[1:]:
            t = self.unify(t, t2, related_points)
        return t


    def unify(self, t1, t2, related_points):
        if t1 in self._vars:
            t1 = self._vars[t1]
        if t2 in self._vars:
            t2 = self._vars[t2]

        if isinstance(t1, PrimType) and isinstance(t2, PrimType):
            if t1 == t2:
                return t1
            raise ConflictingTypeError(related_points, [t1, t2])

        elif isinstance(t1, ArrowType) and isinstance(t2, ArrowType):
            left = self.unify(t1.left, t2.left, related_points)
            right = self.unify(t1.right, t2.right, related_points)
            return ArrowType(left, right)

        elif isinstance(t2, TypeVar):
            self._vars[t2] = t1
            return t1

        elif isinstance(t1, TypeVar):
            self._vars[t1] = t2
            return t2

        else:
            raise ConflictingTypeError(related_points, [t1, t2])


    def infer_types(self, equal_pairs, known_types):
        graph = defaultdict(set)
        for (a, b) in equal_pairs:
            graph[a].add(b)
            graph[b].add(a)

        result = {p: t for p, t in known_types.items()}
        seen = set()

        for key in graph:
            stack = [key]
            types = set()
            related_points = set()

            while stack:
                point = stack.pop()
                related_points.add(point)

                if point in result:
                    types.add(result[point])

                if point in seen:
                    continue
                seen.add(point)

                for child in graph[point]:
                    stack.append(child)

            if types:
                t = self.unify_types(list(types), related_points)
                for p in related_points:
                    result[p] = t
            else:
                raise NoTypeError(related_points)

        return result, self._vars


Int = PrimType('Int')
Float = PrimType('Float')
Bool = PrimType('Bool')


if __name__ == '__main__':
    a = TypeVar('a')
    v1 = TypeVar('1')
    v2 = TypeVar('2')
    v3 = TypeVar('3')
    v4 = TypeVar('4')
    pairs = [(v1, v2), (v3, v4)]

    t1 = ArrowType(Int, Int)
    t2 = ArrowType(Int, a)
    t3 = a
    t4 = Int
    known = {v1: t1, v2: t2, v3: t3, v4: t4}

    result, vs = Context().infer_types(pairs, known)
    print(result)
    print(vs)
