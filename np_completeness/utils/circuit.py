import networkx as nx

from manim.typing import InternalPoint3D, Point3D, Point2D
import numpy as np
import matplotlib.pyplot as plt

from np_completeness.utils.util_general import GATE_HEIGHT


class Gate:
    def __init__(
        self,
        truth_table: dict[tuple[bool], tuple[bool]],
        position: Point3D | Point2D,
        length: float = 1,
    ):
        self.truth_table = truth_table
        self.position: InternalPoint3D = normalize_position(position)
        self.length = length

    @staticmethod
    def make_knot(n_inputs: int, n_outputs: int, position: InternalPoint3D):
        # A mix of True and False values is not supported.
        truth_table = {
            tuple([False] * n_inputs): tuple([False] * n_outputs),
            tuple([True] * n_inputs): tuple([True] * n_outputs),
        }
        return Gate(truth_table, position, length=0)


class Circuit:
    def __init__(self):
        self.g = nx.DiGraph()
        self.gates: dict[str, Gate] = {}
        self.wires: list[tuple[str, str]] = []

    def add_gate(self, name: str, gate: Gate):
        if name in self.gates:
            raise ValueError(f"Gate with name {repr(name)} already exists")

        if "/" in name:
            # This is because when we convert to networkx
            raise ValueError(f"Gate name must not contain slashes, got {repr(name)}")

        self.gates[name] = gate

    def check(self):
        for wire_start, wire_end in self.wires:
            for gate_id in [wire_start, wire_end]:
                if gate_id not in self.gates:
                    raise ValueError(
                        f"Invalid gate id: {gate_id}. Available: {self.gates.keys()}"
                    )

    def to_networkx(self) -> tuple[nx.DiGraph, dict[str, Point2D]]:
        g = nx.DiGraph()

        positions = {}

        for gate in self.gates:
            g.add_node(f"{gate}/in")
            g.add_node(f"{gate}/out")

            positions[f"{gate}/in"] = self.gates[gate].position[:2] + np.array(
                [0, GATE_HEIGHT / 2]
            )
            positions[f"{gate}/out"] = self.gates[gate].position[:2] + np.array(
                [0, -GATE_HEIGHT / 2]
            )

            g.add_edge(f"{gate}/in", f"{gate}/out", length=self.gates[gate].length)

        for wire_start, wire_end in self.wires:
            g.add_edge(
                f"{wire_start}/out",
                f"{wire_end}/in",
                length=self.get_wire_length(wire_start, wire_end),
            )

        return g, positions

    def display_graph(self):
        g, positions = self.to_networkx()

        plt.figure(figsize=(12, 8))
        nx.draw(g, positions, with_labels=True)

        edge_labels = {
            k: round(v, 2) for k, v in nx.get_edge_attributes(g, "length").items()
        }
        nx.draw_networkx_edge_labels(g, positions, edge_labels=edge_labels)

        plt.show()

    def get_wire_length(self, wire_start: str, wire_end: str) -> float:
        return np.linalg.norm(
            self.gates[wire_start].position - self.gates[wire_end].position
        )


def normalize_position(
    position: Point3D | Point2D,
) -> InternalPoint3D:
    if isinstance(position, tuple):
        if len(position) == 2:
            position = np.array([*position, 0])
        elif len(position) == 3:
            position = np.array(position)
        else:
            raise ValueError(f"Invalid position: {position}")
    elif isinstance(position, np.ndarray):
        if position.shape == (2,):
            position = np.array([*position, 0])
        elif position.shape == (3,):
            pass
        else:
            raise ValueError(f"Invalid position: {position}")
    else:
        raise ValueError(f"Invalid position: {position}")

    return position.astype(np.float64)
