from __future__ import annotations

import itertools
from queue import PriorityQueue

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from manim.typing import InternalPoint3D

from np_completeness.utils.gate import Gate, GateEvaluation
from np_completeness.utils.util_general import (
    AnyPoint,
    get_wire_color,
    normalize_position,
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

    def get_simplified_value(self, name: str, reversed: bool = False) -> bool | None:
        """Returns a single value representing the gate's output.

        Multi-output gates are simplified to a single value, using None
        if there's ambiguity.
        """
        gate_inputs = self.get_gate_inputs(name)
        gate_outputs = self.get_gate_outputs(name)

        if reversed:
            gate_inputs, gate_outputs = gate_outputs, gate_inputs

        def simplify(values: tuple[bool, ...]) -> bool | None:
            if not values:
                return None
            else:
                # If any of the values is true, return true. This is not entirely
                # accurate if the output is e.g. (True, False) but it's clearer visually
                # than using None because then the gate would look unvisited.
                return any(values)

        match self.get_gate_outputs(name):
            case ():
                # No outputs
                return simplify(gate_inputs)
            case (single_output,):
                return single_output
            case _:
                # Multi-output gate
                return simplify(gate_outputs)


class Circuit:
    def __init__(self):
        self.g = nx.DiGraph()
        self.gates: dict[str, Gate] = {}
        self.wires: list[tuple[str, str]] = []

    def add_gate(self, name: str, gate: Gate) -> str:
        """Add a gate and, for convenience, return its name."""
        if name in self.gates:
            raise ValueError(f"Gate with name {repr(name)} already exists")

        self.gates[name] = gate

        return name

    def add_wire(
        self,
        wire_start: str,
        wire_end: str,
        knot_positions: list[AnyPoint] | None = None,
    ):
        """Add a wire from `wire_start` to `wire_end`.

        By default, the wire goes directly between the two gates. By adding
        `knot_positions`, the wire will go through the given points. This is
        for readability purposes.
        """
        if wire_start not in self.gates:
            raise ValueError(f"Invalid wire start: {wire_start}")
        if wire_end not in self.gates:
            raise ValueError(f"Invalid wire end: {wire_end}")

        gates = [wire_start]

        for knot_position in knot_positions or []:
            if np.array_equal(
                normalize_position(knot_position), self.gates[gates[-1]].position
            ):
                # The knot is in the same place as the last one, so it's not needed
                continue

            knot_name = self.add_knot(knot_position)
            gates.append(knot_name)

        gates.append(wire_end)

        for start, end in zip(gates, gates[1:]):
            self.wires.append((start, end))

    def add_knot(
        self,
        position: AnyPoint,
        name: str | None = None,
        n_inputs: int = 1,
        n_outputs: int = 1,
    ) -> str:
        if name is None:
            name = f"knot_0"
            for i in range(len(self.gates) + 1):
                if name not in self.gates:
                    break
                name = f"knot_{i}"

            assert name is not None, "Internal error"

        self.add_gate(
            name, Gate.make_knot(position, n_inputs=n_inputs, n_outputs=n_outputs)
        )
        return name

    def position_of(self, name: str) -> InternalPoint3D:
        """Get the position of a gate as a [x, y, 0] NumPy array."""
        return self.gates[name].position

    def x_of(self, name: str) -> float:
        """Get the X position of a gate."""
        return self.gates[name].position[0]

    def y_of(self, name: str) -> float:
        """Get the Y position of a gate."""
        return self.gates[name].position[1]

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
            g.add_node(gate)

            positions[gate] = self.gates[gate].position[:2]

        for wire_start, wire_end in self.wires:
            g.add_edge(
                wire_start,
                wire_end,
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

    def display_graph(self, with_evaluation: bool = True):
        g, positions = self.to_networkx()

        if with_evaluation:
            evaluation = self.evaluate()
        else:
            evaluation = None

        node_color = []
        for gate in g.nodes:
            simplified_value = (
                evaluation.get_simplified_value(gate)
                if evaluation is not None
                else None
            )
            node_color.append(get_wire_color(simplified_value))

        edge_colors = []
        for in_gate, out_gate in g.edges:
            if evaluation is not None:
                wire_value = evaluation.get_wire_value(
                    wire_start=in_gate, wire_end=out_gate
                )
            else:
                wire_value = None

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
            name: gate.reverse(evaluation.gate_evaluations[name])
            for name, gate in self.gates.items()
        }

        reversed.wires = [(wire_end, wire_start) for wire_start, wire_end in self.wires]

        reversed.check()
        return reversed

    def add_missing_inputs_and_outputs(self, visible: bool = True):
        """Add input/output nodes to any gates that don't lead anywhere.

        Useful for debugging.
        """
        # Need to make a copy because we're modifying the dictionary
        gates_to_check = list(self.gates.items())

        for name, gate in gates_to_check:
            n_inputs = len([wire for wire in self.wires if wire[1] == name])
            for i in range(gate.n_inputs - n_inputs):
                self.add_gate(
                    f"input_{name}_{i}",
                    Gate(
                        truth_table={(): (False,)},
                        position=(gate.position + np.array([i * 0.5, 0.5, 0]))
                        if visible
                        else gate.position,
                        visual_type="constant" if visible else "invisible",
                    ),
                )
                self.add_wire(wire_start=f"input_{name}_{i}", wire_end=name)

            n_outputs = len([wire for wire in self.wires if wire[0] == name])
            for i in range(gate.n_outputs - n_outputs):
                self.add_gate(
                    f"output_{name}_{i}",
                    Gate(
                        truth_table={(False,): (), (True,): ()},
                        position=(gate.position + np.array([i * 0.5, -0.5, 0]))
                        if visible
                        else gate.position,
                        visual_type="constant" if visible else "invisible",
                    ),
                )
                self.add_wire(wire_start=name, wire_end=f"output_{name}_{i}")

    def scale(self, factor: float) -> Circuit:
        """Scale the positions of the gates in-place.

        Similar to running .scale() on ManimCircuit(circuit), but the size of the gates
        doesn't change - just the positions.
        """
        for gate in self.gates.values():
            gate.position *= factor

        return self

    def shift(self, shift: InternalPoint3D) -> Circuit:
        """Shift the positions of the gates in-place.

        Should be equivalent to running .shift() on ManimCircuit(circuit).
        """
        for gate in self.gates.values():
            gate.position += shift

        return self


def all_inputs(n_inputs: int) -> list[tuple[bool, ...]]:
    """Return all possible input combinations for `n_inputs`."""
    return list(itertools.product([False, True], repeat=n_inputs))


NOT_TABLE = {
    (False,): (True,),
    (True,): (False,),
}

AND_TABLE = {
    (False, False): (False,),
    (False, True): (False,),
    (True, False): (False,),
    (True, True): (True,),
}

NAND_TABLE = {
    (False, False): (True,),
    (False, True): (True,),
    (True, False): (True,),
    (True, True): (False,),
}

OR_TABLE = {
    (False, False): (False,),
    (False, True): (True,),
    (True, False): (True,),
    (True, True): (True,),
}


OR3_TABLE = {inputs: (any(inputs),) for inputs in all_inputs(3)}


# the output is (lower bit, upper bit = carry)
ADD_TABLE = {
    (False, False, False): (False, False),
    (False, False, True): (True, False),
    (False, True, False): (True, False),
    (False, True, True): (False, True),
    (True, False, False): (True, False),
    (True, False, True): (False, True),
    (True, True, False): (False, True),
    (True, True, True): (True, True),
}
