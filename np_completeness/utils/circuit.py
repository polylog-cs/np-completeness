from queue import PriorityQueue

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from manim.typing import Point2D
from pydantic import BaseModel

from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import GATE_HEIGHT


class GateResult(BaseModel):
    input_values: tuple[bool, ...]
    reach_time: float


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

    def get_gate_inputs(self, name: str) -> list[str]:
        """Return the gates that are inputs to the given gate, in order.

        The order matters for gates that are not commutative.
        """
        relevant_wires = [wire for wire in self.wires if wire[1] == name]

        if len(relevant_wires) != self.gates[name].n_inputs:
            raise ValueError(
                f"Gate {name} has {self.gates[name].n_inputs} inputs, but got "
                f"{len(relevant_wires)} wires"
            )

        return [wire[0] for wire in relevant_wires]

    def get_gate_outputs(self, name: str) -> list[str]:
        """Return the gates that are outputs to the given gate, in order.

        The order matters for gates with multiple outputs that are not commutative.
        """
        relevant_wires = [wire for wire in self.wires if wire[0] == name]

        if len(relevant_wires) != self.gates[name].n_outputs:
            raise ValueError(
                f"Gate {name} has {self.gates[name].n_outputs} outputs, but got "
                f"{len(relevant_wires)} wires"
            )

        return [wire[1] for wire in relevant_wires]

    def to_networkx(self) -> tuple[nx.DiGraph, dict[str, Point2D]]:  # type: ignore[reportMissingTypeArgument]
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

    def get_wire_value(
        self, wire_start: str, wire_end: str, input_values: tuple[bool, ...]
    ) -> bool:
        """Get the value of the wire from wire_start to wire_end.

        Args:
            wire_start: The name of the gate where the wire starts.
            wire_end: The name of the gate where the wire ends.
            input_values: The values of the inputs to `wire_start`.
        """
        truth_table = self.gates[wire_start].truth_table
        outputs = truth_table[input_values]
        output_index = self.get_gate_outputs(wire_start).index(wire_end)

        return outputs[output_index]

    def evaluate(self) -> dict[str, GateResult]:
        """Compute the gates' values and reach times."""
        # (reach time, node name)
        event_queue: PriorityQueue[tuple[float, str]] = PriorityQueue()
        n_inputs_done: dict[str, int] = {name: 0 for name in self.gates}
        evaluation: dict[str, GateResult] = {}

        for name, gate in self.gates.items():
            # Start from the nodes that have no inputs
            if gate.n_inputs == 0:
                event_queue.put((0, name))
                n_inputs_done[name] = -1

        while not event_queue.empty():
            time, name = event_queue.get()
            n_inputs_done[name] += 1

            # If we've already visited from all of its inputs
            if n_inputs_done[name] == self.gates[name].n_inputs:
                for output_name in self.get_gate_outputs(name):
                    event_queue.put(
                        (time + self.get_wire_length(name, output_name), output_name)
                    )

                gate_inputs = self.get_gate_inputs(name)
                input_values = []
                for input_name in gate_inputs:
                    value = self.get_wire_value(
                        wire_start=input_name,
                        wire_end=name,
                        input_values=evaluation[input_name].input_values,
                    )
                    input_values.append(value)

                evaluation[name] = GateResult(
                    input_values=tuple(input_values), reach_time=time
                )

        return evaluation

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
        distance = np.linalg.norm(
            self.gates[wire_start].position - self.gates[wire_end].position
        )
        # Round for legibility when debugging.
        return round(float(distance), 2)
