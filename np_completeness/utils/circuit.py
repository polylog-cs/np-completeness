from typing import Any

from manim import *

# Imported for the side effect of changing the default colors
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import (
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
