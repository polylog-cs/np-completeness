# So that we can reference the class in the class definition
from __future__ import annotations

from dataclasses import dataclass, field
from queue import PriorityQueue


@dataclass
class Node:
    inputs: list[int] = field(default_factory=list)
    # (node, edge length)
    outputs: list[tuple[int, float]] = field(default_factory=list)
    reach_time: float | None = None
    n_inputs_done: int = 0

    def __str__(self):
        return (
            f"Node(inputs={self.inputs}, outputs={self.outputs}, "
            f"reach_time={self.reach_time}, n_inputs_done={self.n_inputs_done})"
        )


class SignalPropagation:
    def __init__(self):
        self.nodes: list[Node] = []

    def add_node(self, node: Node | None = None):
        """Add a node to the graph."""
        self.nodes.append(node or Node())

    def add_edge(self, node_from: Node | int, node_to: Node | int, length: float):
        """Add an edge to the graph as either node objects or node indices."""
        if isinstance(node_from, Node):
            node_from = self.nodes.index(node_from)
        if isinstance(node_to, Node):
            node_to = self.nodes.index(node_to)

        self.nodes[node_from].outputs.append((node_to, length))
        self.nodes[node_to].inputs.append(node_from)

    def propagate(self):
        for node in self.nodes:
            node.reach_time = None
            node.n_inputs_done = 0

        # (reach time, node index)
        event_queue: PriorityQueue[tuple[float, int]] = PriorityQueue()

        for i, node in enumerate(self.nodes):
            # Start from the nodes that have no inputs
            if not node.inputs:
                event_queue.put((0, i))
                node.n_inputs_done = -1

        for node in self.nodes:
            print(node)

        while not event_queue.empty():
            time, node_index = event_queue.get()
            print(time, node_index)
            node = self.nodes[node_index]
            node.n_inputs_done += 1

            if node.n_inputs_done == len(node.inputs):
                # Already visited from all of its inputs
                node.reach_time = time

                for next_node_i, edge_length in node.outputs:
                    event_queue.put((time + edge_length, next_node_i))
