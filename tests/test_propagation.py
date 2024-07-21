from np_completeness.utils.propagation import Node, SignalPropagation


def test_propagation():
    sp = SignalPropagation()
    nodes = [Node() for _ in range(5)]
    for node in nodes:
        sp.add_node(node)

    edges = [
        (0, 1, 1.0),
        (1, 3, 1.0),
        (2, 3, 1.0),
        (3, 4, 1.5),
    ]
    for node_from, node_to, length in edges:
        sp.add_edge(node_from, node_to, length)

    sp.propagate()
    assert [node.reach_time for node in sp.nodes] == [0.0, 1.0, 0.0, 2.0, 3.5]

    # Test that we're idempotent
    sp.propagate()
    assert [node.reach_time for node in sp.nodes] == [0.0, 1.0, 0.0, 2.0, 3.5]
