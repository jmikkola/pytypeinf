from collections import defaultdict

def topological_order(edge_list):
    '''
    [('a', 'b')] means that b depends on a, and a
    should come first in the output.
    '''

    children = defaultdict(set)
    counts = defaultdict(int)
    nodes = set()

    for a, b in edge_list:
        nodes.add(a)
        nodes.add(b)
        children[a].add(b)
        counts[b] += 1

    order = []
    stack = []

    for node in nodes:
        if counts[node] == 0:
            stack.append(node)

    visited = set()
    while stack:
        node = stack.pop()
        visited.add(node)
        order.append(node)

        for child in children[node]:
            counts[child] -= 1
            if counts[child] == 0:
                stack.append(child)

    if len(order) < len(nodes):
        return False
    return order
