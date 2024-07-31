from typing import cast

from manim import *
from manim.typing import InternalPoint3D

# Imported for the side effect of changing the default colors
from np_completeness.utils.old_circuit import OldCircuit
from np_completeness.utils.old_gate import AndGate
from np_completeness.utils.old_wire import OldWire
from np_completeness.utils.util_general import (
    GATE_HEIGHT,
    GATE_HORIZONTAL_SPACING,
    GATE_VERTICAL_SPACING,
    GATE_WIDTH,
)


def make_multiplication_circuit() -> OldCircuit:
    circuit = OldCircuit()

    # first we create 4x4 and gates
    for i in range(4):
        for j in range(4):
            and_gate = AndGate()
            and_gate.set_z_index(3)  # Make sure the gates are in front of the wires
            and_gate.move_to(
                (i + j) * GATE_HORIZONTAL_SPACING * LEFT
                + i * GATE_VERTICAL_SPACING * DOWN
                + 2 * UP
                + 4 * RIGHT
            )
            circuit.add_gate(and_gate)
            out_wire = OldWire(
                cast(InternalPoint3D, and_gate.get_bottom()),
                and_gate.get_bottom() + 0.3 * GATE_HEIGHT * DOWN,
            )
            and_gate.output = out_wire
            circuit.add_output_wire(out_wire)

    # create the 8 input wires
    for t in range(2):
        for i in range(4):
            input_wire = OldWire(
                circuit.gates[i].left_input_position()
                + t * 0.3 * GATE_WIDTH * RIGHT
                + (t + 1) * GATE_HEIGHT * UP,
                circuit.gates[i].left_input_position()
                + t * 0.3 * GATE_WIDTH * RIGHT
                + (t + 0.3) * GATE_HEIGHT * UP,
            )
            circuit.add_input_wire(input_wire)

    # start from the first four output wires and connect them to the appropriate gates
    last_wires = circuit.input_wires[:4]
    for i in range(4):
        for j in range(4):
            # first add a short wire connecting the last wire to the appropriate gate
            short_wire = OldWire(
                last_wires[j].end_point, circuit.gates[i * 4 + j].left_input_position()
            )
            last_wires[j].add_output_wire(short_wire)
            short_wire.add_input_wire(last_wires[j])
            circuit.gates[i * 4 + j].inputs.append(short_wire)
            circuit.add_wire(short_wire)

            if i == 3:
                continue

            # then add a wire going to the left
            left_wire = OldWire(
                last_wires[j].end_point,
                last_wires[j].end_point
                + (1 / 3 * GATE_WIDTH + 1 / 2 * (GATE_HORIZONTAL_SPACING - GATE_WIDTH))
                * LEFT,
            )
            last_wires[j].add_output_wire(left_wire)
            left_wire.add_input_wire(last_wires[j])
            circuit.add_wire(left_wire)

            # next wire goes down
            down_wire = OldWire(
                left_wire.end_point,
                left_wire.end_point + 0.9 * GATE_VERTICAL_SPACING * DOWN,
            )
            left_wire.add_output_wire(down_wire)
            down_wire.add_input_wire(left_wire)
            circuit.add_wire(down_wire)

            # next wire is diagonal
            diagonal_wire = OldWire(
                down_wire.end_point,
                down_wire.end_point
                + 0.1 * GATE_VERTICAL_SPACING * DOWN
                + 0.1 * GATE_HORIZONTAL_SPACING * LEFT,
            )
            down_wire.add_output_wire(diagonal_wire)
            diagonal_wire.add_input_wire(down_wire)
            circuit.add_wire(diagonal_wire)

            # final wire goes to the left again
            last_wire = OldWire(
                diagonal_wire.end_point,
                circuit.gates[(i + 1) * 4 + j].left_input_position()
                + 0.3 * GATE_HEIGHT * UP,
            )
            diagonal_wire.add_output_wire(last_wire)
            last_wire.add_input_wire(diagonal_wire)
            circuit.add_wire(last_wire)

            last_wires[j] = last_wire

    # next we do the other four input wires
    for i in range(4):
        first_wire = OldWire(
            circuit.input_wires[4 + i].end_point,
            circuit.gates[4 * i].right_input_position() + 0.6 * GATE_HEIGHT * UP,
        )
        circuit.input_wires[4 + i].add_output_wire(first_wire)
        first_wire.add_input_wire(circuit.input_wires[4 + i])
        circuit.add_wire(first_wire)

        last_wire = first_wire
        left_wires = []
        for j in range(3):
            left_wire = OldWire(
                last_wire.end_point,
                last_wire.end_point + GATE_HORIZONTAL_SPACING * LEFT,
            )
            last_wire.add_output_wire(left_wire)
            left_wire.add_input_wire(last_wire)
            circuit.add_wire(left_wire)
            left_wires.append(left_wire)
            last_wire = left_wire

        for j, wire in enumerate([first_wire] + left_wires):
            down_wire = OldWire(
                wire.end_point, circuit.gates[4 * i + j].right_input_position()
            )
            wire.add_output_wire(down_wire)
            down_wire.add_input_wire(wire)
            circuit.gates[4 * i + j].inputs.append(down_wire)
            circuit.add_wire(down_wire)

    return circuit


class CircuitScene(Scene):
    def construct(self):
        circuit = make_multiplication_circuit()
        self.add(circuit)

        circuit.create(self, 10)

        circuit.run_forward(
            self, [True, False, True, True, False, True, False, True], 10
        )

        circuit.reset(self)
        self.wait()

        circuit.run_backward(
            self, [False, False, False, True, True, True, False, True], 10
        )

        return


if __name__ == "__main__":
    pass
    # scene = CircuitScene()
    # scene.render()

    # circuit = make_multiplication_circuit()
