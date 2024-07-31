from __future__ import annotations

from queue import PriorityQueue

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from manim.typing import Point2D

from np_completeness.utils.gate import Gate, GateEvaluation
from np_completeness.utils.util_general import (
    GATE_HEIGHT,
    get_wire_color,
)


class CircuitEvaluation:
    def __init__(
        self,
        circuit: "Circuit",
    ):
        self.circuit = circuit
        self.gate_evaluations: dict[str, GateEvaluation] = {}

    def get_wire_value(self, wire_start: str, wire_end: str) -> bool:
        """Get the value of the wire from wire_start to wire_end.

        Args:
            wire_start: The name of the gate where the wire starts.
            wire_end: The name of the gate where the wire ends.
            input_values: The values of the inputs to `wire_start`.
        """
        truth_table = self.circuit.gates[wire_start].truth_table
        outputs = truth_table[self.gate_evaluations[wire_start].input_values]
        output_index = self.circuit.get_successors(wire_start).index(wire_end)

        return outputs[output_index]

    def get_gate_outputs(self, name: str) -> tuple[bool, ...]:
        input_values = self.gate_evaluations[name].input_values
        return self.circuit.gates[name].truth_table[input_values]

    def get_gate_inputs(self, name: str) -> tuple[bool, ...]:
        # Convenience method for symmetry with get_gate_outputs()
        return self.gate_evaluations[name].input_values

    def get_simplified_value(self, name: str) -> bool | None:
        """Returns a single value representing the gate's output.

        Multi-output gates are simplified to a single value, using None
        if there's ambiguity.
        """
        gate_outputs = self.get_gate_outputs(name)

        match self.get_gate_outputs(name):
            case (single_output,):
                return single_output
            case _:
                # Multi-output gate
                if all(gate_outputs):
                    return True
                elif all(not output for output in gate_outputs):
                    return False
                else:
                    return None


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

    def get_predecessors(self, gate_name: str) -> list[str]:
        """Return the gates that are inputs to the given gate, in order.

        The order matters for gates that are not commutative.
        """
        relevant_wires = [wire for wire in self.wires if wire[1] == gate_name]

        if len(relevant_wires) != self.gates[gate_name].n_inputs:
            raise ValueError(
                f"Gate {gate_name} has {self.gates[gate_name].n_inputs} inputs, but got "
                f"{len(relevant_wires)} wires"
            )

        return [wire[0] for wire in relevant_wires]

    def get_successors(self, gate_name: str) -> list[str]:
        """Return the gates that are outputs to the given gate, in order.

        The order matters for gates with multiple outputs that are not commutative.
        """
        relevant_wires = [wire for wire in self.wires if wire[0] == gate_name]

        if len(relevant_wires) != self.gates[gate_name].n_outputs:
            raise ValueError(
                f"Gate {gate_name} has {self.gates[gate_name].n_outputs} outputs, but got "
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

    def evaluate(self) -> CircuitEvaluation:
        """Compute the gates' values and reach times."""
        # (reach time, node name)
        event_queue: PriorityQueue[tuple[float, str]] = PriorityQueue()
        n_inputs_done: dict[str, int] = {name: 0 for name in self.gates}
        evaluation = CircuitEvaluation(circuit=self)

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
                for output_name in self.get_successors(name):
                    event_queue.put(
                        (
                            time
                            + self.get_wire_length(name, output_name)
                            # This is when the wire starts filling,
                            # so we add the gate's length
                            + self.gates[name].length,
                            output_name,
                        )
                    )

                gate_inputs = self.get_predecessors(name)
                input_values = []
                for input_name in gate_inputs:
                    value = evaluation.get_wire_value(
                        wire_start=input_name,
                        wire_end=name,
                    )
                    input_values.append(value)

                evaluation.gate_evaluations[name] = GateEvaluation(
                    input_values=tuple(input_values), reach_time=time
                )

        return evaluation

    def display_graph(self):
        g, positions = self.to_networkx()
        evaluation = self.evaluate()

        node_color = []
        for node in g.nodes:
            gate = node.removesuffix("/out").removesuffix("/in")
            gate_outputs = evaluation.get_gate_outputs(gate)

            match gate_outputs:
                case (single_output,):
                    node_color.append(get_wire_color(single_output))
                case _:
                    # Multi-output gate
                    if all(gate_outputs):
                        node_color.append(get_wire_color(True))
                    elif all(not output for output in gate_outputs):
                        node_color.append(get_wire_color(False))
                    else:
                        node_color.append(get_wire_color(None))

        edge_colors = []
        for in_node, out_node in g.edges:
            if in_node.endswith("/in") and out_node.endswith("/out"):
                # Internal gate edge
                edge_colors.append(get_wire_color(None))
                continue

            in_gate = in_node.removesuffix("/out")
            out_gate = out_node.removesuffix("/in")

            wire_value = evaluation.get_wire_value(
                wire_start=in_gate, wire_end=out_gate
            )
            edge_colors.append(get_wire_color(wire_value))

        plt.figure(figsize=(12, 8))

        nx.draw(
            g,
            positions,
            with_labels=True,
            node_color=node_color,
            edge_color=edge_colors,
            width=2,
        )

        plt.show()

    def get_wire_length(self, wire_start: str, wire_end: str) -> float:
        distance = np.linalg.norm(
            self.gates[wire_start].position - self.gates[wire_end].position
        )
        # Round for legibility when debugging.
        return round(float(distance), 2)

    def reverse(self) -> Circuit:
        evaluation = self.evaluate()

        reversed = Circuit()
        reversed.gates = {
            name: gate.invert(evaluation.gate_evaluations[name])
            for name, gate in self.gates.items()
        }

        reversed.wires = [(wire_end, wire_start) for wire_start, wire_end in self.wires]

        reversed.check()
        return reversed
