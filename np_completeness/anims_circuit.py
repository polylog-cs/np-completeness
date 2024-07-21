from typing import Any, cast

from manim import *
from manim.typing import InternalPoint3D

# Imported for the side effect of changing the default colors
from np_completeness.utils.gate import AndGate, Gate
from np_completeness.utils.util_general import (
    GATE_HEIGHT,
    GATE_HORIZONTAL_SPACING,
    GATE_VERTICAL_SPACING,
    GATE_WIDTH,
    WIRE_COLOR_NONE,
)
from np_completeness.utils.wire import Wire


class Circuit(VGroup):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.gates: list[Gate] = []
        self.wires: list[Wire] = []
        self.input_wires: list[Wire] = []
        self.output_wires: list[Wire] = []

    def add_gate(self, gate: Gate):
        self.gates.append(gate)
        self.add(gate)

    def add_wire(self, wire: Wire):
        self.wires.append(wire)
        self.add(wire)

    def add_input_wire(self, wire: Wire):
        self.input_wires.append(wire)
        self.add_wire(wire)

    def add_output_wire(self, wire: Wire):
        self.output_wires.append(wire)
        self.add_wire(wire)

    def get_all_wires(self) -> list[Wire]:
        return self.input_wires + self.wires + self.output_wires

    def create(self, scene: Scene, duration: float):
        # creates the circuit similarly to run_forward function

        # first change activation_animation to True for all wires and gates

        for wire in self.wires:
            wire.activation_animation = True
            wire.active = False
            scene.add(wire)

        for gate in self.gates:
            gate.activation_animation = True
            scene.add(gate)

        # activate input wires
        for wire in self.input_wires:
            wire.active = True

        scene.wait(duration)

        # for wire in self.wires:
        #     wire.activation_animation = True
        # for gate in self.gates:
        #     gate.activation_animation = True

    def run_forward(self, scene: Scene, inputs: list[bool], duration: float = 10):
        self._remove_updaters(scene)
        if len(inputs) != len(self.input_wires):
            raise ValueError("Number of inputs must match number of input wires")

        for wire in self.wires:
            wire.set_value(None)
            wire.is_forward = True

        for gate in self.gates:
            gate.activated = False

        for wire, value in zip(self.input_wires, inputs):
            wire.set_value(value)

        for wire in self.wires:
            scene.add_updater(wire.propagate_signal)

        for gate in self.gates:
            scene.add_updater(gate.update_forward)

        scene.wait(duration)

    def run_backward(self, scene: Scene, inputs: list[bool], duration: float = 10):
        self._remove_updaters(scene)

        for wire in self.wires:
            wire.set_value(None)
            wire.is_forward = False

        for gate in self.gates:
            gate.activated = False

        # set the values of wires to their rightful values
        self._run_forward_internal(inputs)

        for wire in self.output_wires:
            wire.set_value(wire._future_value)

        for wire in self.wires:
            scene.add_updater(wire.propagate_signal_back)

        for gate in self.gates:
            scene.add_updater(gate.update_backward)

        scene.wait(duration)

    def _run_forward_internal(self, inputs: list[bool]):
        for wire in self.wires:
            wire._future_value = None

        # Set input values
        for wire, value in zip(self.input_wires, inputs):
            wire._future_value = value

        # Keep track of gates that have been evaluated
        evaluated_gates = set()

        while len(evaluated_gates) < len(self.gates):
            for gate in self.gates:
                if gate not in evaluated_gates and all(
                    input_wire._future_value is not None for input_wire in gate.inputs
                ):
                    output_value = gate.evaluate()
                    if gate.output:
                        gate.output._future_value = output_value
                    evaluated_gates.add(gate)
            for wire in self.wires:
                if wire.input_wire and wire.input_wire._future_value is not None:
                    wire._future_value = wire.input_wire._future_value

    def _remove_updaters(self, scene: Scene):
        for wire in self.wires:
            scene.remove_updater(wire.propagate_signal)
            scene.remove_updater(wire.propagate_signal_back)
        for gate in self.gates:
            scene.remove_updater(gate.update_forward)
            scene.remove_updater(gate.update_backward)

    def reset(self, scene: Scene):
        anims = []
        for wire in self.wires:
            anims.append(wire.active_part.animate.set_color(WIRE_COLOR_NONE))
            anims.append(wire.active_part_back.animate.set_color(WIRE_COLOR_NONE))
        for gate in self.gates:
            anims.append(gate.animate.set_fill(WIRE_COLOR_NONE))
        scene.play(*anims)

        # first set the length to 0 and only then remove the updaters

        for wire in self.wires:
            wire.progress.set_value(0.001)
            wire.progress_back.set_value(0.001)
        scene.wait(0.001)

        for wire in self.wires:
            wire.progress.set_value(0)
            wire.progress_back.set_value(0)

        for wire in self.wires:
            wire.value = None
            scene.remove_updater(wire.propagate_signal)
            scene.remove_updater(wire.propagate_signal_back)

        for gate in self.gates:
            gate.activated = False
            scene.remove_updater(gate.update_forward)
            scene.remove_updater(gate.update_backward)


def make_multiplication_circuit() -> Circuit:
    circuit = Circuit()

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
            out_wire = Wire(
                cast(InternalPoint3D, and_gate.get_bottom()),
                and_gate.get_bottom() + 0.3 * GATE_HEIGHT * DOWN,
            )
            and_gate.output = out_wire
            circuit.add_output_wire(out_wire)

    # create the 8 input wires
    for t in range(2):
        for i in range(4):
            input_wire = Wire(
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
            short_wire = Wire(
                last_wires[j].end_point, circuit.gates[i * 4 + j].left_input_position()
            )
            last_wires[j].add_output_wire(short_wire)
            short_wire.add_input_wire(last_wires[j])
            circuit.gates[i * 4 + j].inputs.append(short_wire)
            circuit.add_wire(short_wire)

            if i == 3:
                continue

            # then add a wire going to the left
            left_wire = Wire(
                last_wires[j].end_point,
                last_wires[j].end_point
                + (1 / 3 * GATE_WIDTH + 1 / 2 * (GATE_HORIZONTAL_SPACING - GATE_WIDTH))
                * LEFT,
            )
            last_wires[j].add_output_wire(left_wire)
            left_wire.add_input_wire(last_wires[j])
            circuit.add_wire(left_wire)

            # next wire goes down
            down_wire = Wire(
                left_wire.end_point,
                left_wire.end_point + 0.9 * GATE_VERTICAL_SPACING * DOWN,
            )
            left_wire.add_output_wire(down_wire)
            down_wire.add_input_wire(left_wire)
            circuit.add_wire(down_wire)

            # next wire is diagonal
            diagonal_wire = Wire(
                down_wire.end_point,
                down_wire.end_point
                + 0.1 * GATE_VERTICAL_SPACING * DOWN
                + 0.1 * GATE_HORIZONTAL_SPACING * LEFT,
            )
            down_wire.add_output_wire(diagonal_wire)
            diagonal_wire.add_input_wire(down_wire)
            circuit.add_wire(diagonal_wire)

            # final wire goes to the left again
            last_wire = Wire(
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
        first_wire = Wire(
            circuit.input_wires[4 + i].end_point,
            circuit.gates[4 * i].right_input_position() + 0.6 * GATE_HEIGHT * UP,
        )
        circuit.input_wires[4 + i].add_output_wire(first_wire)
        first_wire.add_input_wire(circuit.input_wires[4 + i])
        circuit.add_wire(first_wire)

        last_wire = first_wire
        left_wires = []
        for j in range(3):
            left_wire = Wire(
                last_wire.end_point,
                last_wire.end_point + GATE_HORIZONTAL_SPACING * LEFT,
            )
            last_wire.add_output_wire(left_wire)
            left_wire.add_input_wire(last_wire)
            circuit.add_wire(left_wire)
            left_wires.append(left_wire)
            last_wire = left_wire

        for j, wire in enumerate([first_wire] + left_wires):
            down_wire = Wire(
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
    scene = CircuitScene()
    scene.render()
