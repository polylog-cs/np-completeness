from manim import *

GATE_WIDTH = 1
GATE_HEIGHT = 0.5
SIGNAL_SPEED = 0.5  # units per second
WIRE_COLOR = WHITE
GATE_TEXT_RATIO = 0.6
EPSILON = 1e-6
GATE_HORIZONTAL_SPACING = 1.5
GATE_VERTICAL_SPACING = 1


class Wire(VMobject):
    def __init__(self, start, end, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start
        self.end_point = end
        self.length = np.linalg.norm(end - start)
        self.value = None
        self.future_value = None
        self.is_forward = True
        self.input_wire = None
        self.output_wires = []

        self.line = Line(start, end, color=WIRE_COLOR)
        self.add(self.line)
        self.offset = 1e-6 * (end - start)

        self.activation_animation = False
        self.active = False
        self.activate_progress = ValueTracker(0)
        self.add_updater(self.update_create)

        self.progress = ValueTracker(0)
        self.active_part = Line(start, start + self.offset, color=WIRE_COLOR)
        self.add(self.active_part)
        self.add_updater(self.update_active_part)

        self.progress_back = ValueTracker(0)
        self.active_part_back = Line(end - self.offset, end, color=WIRE_COLOR)
        self.add(self.active_part_back)
        self.add_updater(self.update_active_part_back)

    def add_input_wire(self, wire):
        self.input_wire = wire

    def add_output_wire(self, wire):
        self.output_wires.append(wire)

    def set_value(self, value):
        self.value = value
        color = RED if value else BLUE
        self.active_part.set_color(color)
        self.active_part_back.set_color(color)
        self.progress.set_value(0)
        self.progress_back.set_value(0)
        self.active_part.put_start_and_end_on(
            self.start_point, self.start_point + self.offset
        )
        self.active_part_back.put_start_and_end_on(
            self.end_point - self.offset, self.end_point
        )

    def update_create(self, mobject, dt):
        if self.activation_animation:
            if self.active:
                self.activate_progress.set_value(
                    min(
                        self.activate_progress.get_value()
                        + dt * SIGNAL_SPEED / self.length,
                        1,
                    )
                )
            else:
                self.activate_progress.set_value(0)
            alpha = self.activate_progress.get_value()
            end = (1 - alpha) * self.start_point + alpha * self.end_point
            self.line.put_start_and_end_on(self.start_point, end + self.offset)

            if alpha == 1:
                for wire in self.output_wires:
                    wire.active = True

    def update_active_part(self, mob, dt):
        if self.is_forward:
            alpha = self.progress.get_value()
            if alpha > 0:
                end = self.line.point_from_proportion(alpha)
                self.active_part.put_start_and_end_on(self.start_point, end)
            if alpha == 1:
                for wire in self.output_wires:
                    if wire.value is None:
                        wire.set_value(self.value)

    def update_active_part_back(self, mob, dt):
        if not self.is_forward:
            alpha = self.progress_back.get_value()
            if alpha > 0:
                start = self.line.point_from_proportion(1 - alpha)
                self.active_part_back.put_start_and_end_on(start, self.end_point)
            if alpha == 1:
                if self.input_wire is not None and self.input_wire.value is None:
                    self.input_wire.set_value(self.value)

    def propagate_signal(self, dt):
        if self.value is not None:
            self.progress.set_value(
                min(self.progress.get_value() + dt * SIGNAL_SPEED / self.length, 1)
            )

    def propagate_signal_back(self, dt):
        if self.value is not None:
            self.progress_back.set_value(
                min(self.progress_back.get_value() + dt * SIGNAL_SPEED / self.length, 1)
            )


class Gate(VMobject):
    def __init__(self, gate_type, inputs=None, output=None, **kwargs):
        super().__init__(**kwargs)
        self.gate_type = gate_type
        self.inputs = inputs if inputs is not None else []
        self.output = output

        self.rect = Rectangle(height=GATE_HEIGHT, width=GATE_WIDTH, fill_opacity=0.5)
        self.text = (
            Text(gate_type)
            .move_to(self.rect.get_center())
            .scale_to_fit_height(GATE_HEIGHT * GATE_TEXT_RATIO)
        )

        self.add(self.rect, self.text)

        self.activated = False
        self.activation_animation = False
        self.active = False
        self.activate_progress = ValueTracker(0)
        self.add_updater(self.update_create)

    def update_create(self, mobject, dt):
        if self.activation_animation:
            if not self.active and all(
                input_wire.activate_progress.get_value() == 1
                for input_wire in self.inputs
            ):
                self.active = True
                if self.output:
                    self.output.active = True

            if self.active:
                self.activate_progress.set_value(
                    min(self.activate_progress.get_value() + dt * SIGNAL_SPEED, 1)
                )
            else:
                self.activate_progress.set_value(0)

            alpha = self.activate_progress.get_value()
            self.rect.scale_to_fit_height(GATE_HEIGHT * alpha + EPSILON)
            self.text.move_to(self.rect.get_center()).scale_to_fit_height(
                self.rect.height * GATE_TEXT_RATIO
            )

    def add_input(self, wire):
        self.inputs.append(wire)

    def set_output(self, wire):
        self.output = wire

    def evaluate(self):
        raise NotImplementedError("Subclasses must implement this method")

    def activate(self, dt):
        if not self.activated and all(
            input_wire.progress.get_value() == 1 for input_wire in self.inputs
        ):
            self.activated = True
            output_value = self.evaluate()
            self.rect.set_fill(RED if output_value else BLUE)
            if self.output:
                self.output.set_value(output_value)

    def activate_back(self, dt):
        if (
            not self.activated
            and self.output
            and self.output.progress_back.get_value() >= 0.99
        ):
            self.activated = True
            output_value = self.output.value
            self.rect.set_fill(RED if output_value else BLUE)
            for input_wire in self.inputs:
                input_wire.set_value(input_wire.future_value)

    def left_input_position(self):
        return self.rect.get_top() + GATE_WIDTH / 6 * LEFT

    def right_input_position(self):
        return self.rect.get_top() + GATE_WIDTH / 6 * RIGHT


class AndGate(Gate):
    def __init__(self, **kwargs):
        super().__init__("AND", **kwargs)

    def evaluate(self):
        return all(wire.value for wire in self.inputs)


class OrGate(Gate):
    def __init__(self, **kwargs):
        super().__init__("OR", **kwargs)

    def evaluate(self):
        return any(wire.value for wire in self.inputs)


class Circuit(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gates = []
        self.wires = []
        self.input_wires = []
        self.output_wires = []

    def add_gate(self, gate):
        self.gates.append(gate)
        self.add(gate)

    def add_wire(self, wire):
        self.wires.append(wire)
        self.add(wire)

    def add_input_wire(self, wire):
        self.input_wires.append(wire)
        self.add_wire(wire)

    def add_output_wire(self, wire):
        self.output_wires.append(wire)
        self.add_wire(wire)

    def create(self, scene, duration):
        # creates the circuit similarly to run_forward function

        # first change activation_animation to True for all wires and gates

        for wire in self.wires:
            wire.activation_animation = True
            wire.active = False
            scene.add(wire)

        for gate in self.gates:
            gate.activation_animation = True
            gate.done = False
            scene.add(gate)

        # activate input wires
        for wire in self.input_wires:
            wire.active = True

        scene.wait(duration)

        # for wire in self.wires:
        #     wire.activation_animation = True
        # for gate in self.gates:
        #     gate.activation_animation = True

    def run_forward(self, scene, inputs, duration=10):
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
            scene.add_updater(gate.activate)

        scene.wait(duration)

    def run_backward(self, scene, inputs, duration=10):
        self._remove_updaters(scene)

        for wire in self.wires:
            wire.set_value(None)
            wire.is_forward = False

        for gate in self.gates:
            gate.activated = False

        # set the values of wires to their rightful values
        self._run_forward_internal(inputs)

        for wire in self.output_wires:
            wire.set_value(wire.future_value)

        for wire in self.wires:
            scene.add_updater(wire.propagate_signal_back)

        for gate in self.gates:
            scene.add_updater(gate.activate_back)

        scene.wait(duration)

    def _run_forward_internal(self, inputs):
        for wire in self.wires:
            wire.future_value = None  # variable is used only internally

        # Set input values
        for wire, value in zip(self.input_wires, inputs):
            wire.future_value = value

        # Keep track of gates that have been evaluated
        evaluated_gates = set()

        while len(evaluated_gates) < len(self.gates):
            for gate in self.gates:
                if gate not in evaluated_gates and all(
                    input_wire.future_value is not None for input_wire in gate.inputs
                ):
                    output_value = gate.evaluate()
                    if gate.output:
                        gate.output.future_value = output_value
                    evaluated_gates.add(gate)
            for wire in self.wires:
                if wire.input_wire and wire.input_wire.future_value is not None:
                    wire.future_value = wire.input_wire.future_value

    def _remove_updaters(self, scene):
        for wire in self.wires:
            scene.remove_updater(wire.propagate_signal)
            scene.remove_updater(wire.propagate_signal_back)
        for gate in self.gates:
            scene.remove_updater(gate.activate)
            scene.remove_updater(gate.activate_back)

    def reset(self, scene):
        anims = []
        for wire in self.wires:
            anims.append(wire.active_part.animate.set_color(WIRE_COLOR))
            anims.append(wire.active_part_back.animate.set_color(WIRE_COLOR))
        for gate in self.gates:
            anims.append(gate.animate.set_fill(WIRE_COLOR))
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
            scene.remove_updater(gate.activate)
            scene.remove_updater(gate.activate_back)


class MultiplicationCircuit(Circuit):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # first we create 4x4 and gates
        for i in range(4):
            for j in range(4):
                and_gate = AndGate()
                and_gate.move_to(
                    (i + j) * GATE_HORIZONTAL_SPACING * LEFT
                    + i * GATE_VERTICAL_SPACING * DOWN
                    + 2 * UP
                    + 4 * RIGHT
                )
                self.add_gate(and_gate)
                out_wire = Wire(
                    and_gate.get_bottom(),
                    and_gate.get_bottom() + 0.3 * GATE_HEIGHT * DOWN,
                )
                and_gate.set_output(out_wire)
                self.add_output_wire(out_wire)

        # create the 8 input wires
        for t in range(2):
            for i in range(4):
                input_wire = Wire(
                    self.gates[i].left_input_position()
                    + t * 0.3 * GATE_WIDTH * RIGHT
                    + (t + 1) * GATE_HEIGHT * UP,
                    self.gates[i].left_input_position()
                    + t * 0.3 * GATE_WIDTH * RIGHT
                    + (t + 0.3) * GATE_HEIGHT * UP,
                )
                self.add_input_wire(input_wire)

        # start from the first four output wires and connect them to the appropriate gates
        last_wires = self.input_wires[:4]
        for i in range(4):
            for j in range(4):
                # first add a short wire connecting the last wire to the appropriate gate
                short_wire = Wire(
                    last_wires[j].end_point, self.gates[i * 4 + j].left_input_position()
                )
                last_wires[j].add_output_wire(short_wire)
                short_wire.add_input_wire(last_wires[j])
                self.gates[i * 4 + j].add_input(short_wire)
                self.add_wire(short_wire)

                if i == 3:
                    continue

                # then add a wire going to the left
                left_wire = Wire(
                    last_wires[j].end_point,
                    last_wires[j].end_point
                    + (
                        1 / 3 * GATE_WIDTH
                        + 1 / 2 * (GATE_HORIZONTAL_SPACING - GATE_WIDTH)
                    )
                    * LEFT,
                )
                last_wires[j].add_output_wire(left_wire)
                left_wire.add_input_wire(last_wires[j])
                self.add_wire(left_wire)

                # next wire goes down
                down_wire = Wire(
                    left_wire.end_point,
                    left_wire.end_point + 0.9 * GATE_VERTICAL_SPACING * DOWN,
                )
                left_wire.add_output_wire(down_wire)
                down_wire.add_input_wire(left_wire)
                self.add_wire(down_wire)

                # next wire is diagonal
                diagonal_wire = Wire(
                    down_wire.end_point,
                    down_wire.end_point
                    + 0.1 * GATE_VERTICAL_SPACING * DOWN
                    + 0.1 * GATE_HORIZONTAL_SPACING * LEFT,
                )
                down_wire.add_output_wire(diagonal_wire)
                diagonal_wire.add_input_wire(down_wire)
                self.add_wire(diagonal_wire)

                # final wire goes to the left again
                last_wire = Wire(
                    diagonal_wire.end_point,
                    self.gates[(i + 1) * 4 + j].left_input_position()
                    + 0.3 * GATE_HEIGHT * UP,
                )
                diagonal_wire.add_output_wire(last_wire)
                last_wire.add_input_wire(diagonal_wire)
                self.add_wire(last_wire)

                last_wires[j] = last_wire

        # next we do the other four input wires
        for i in range(4):
            first_wire = Wire(
                self.input_wires[4 + i].end_point,
                self.gates[4 * i].right_input_position() + 0.6 * GATE_HEIGHT * UP,
            )
            self.input_wires[4 + i].add_output_wire(first_wire)
            first_wire.add_input_wire(self.input_wires[4 + i])
            self.add_wire(first_wire)

            last_wire = first_wire
            left_wires = []
            for j in range(3):
                left_wire = Wire(
                    last_wire.end_point,
                    last_wire.end_point + GATE_HORIZONTAL_SPACING * LEFT,
                )
                last_wire.add_output_wire(left_wire)
                left_wire.add_input_wire(last_wire)
                self.add_wire(left_wire)
                left_wires.append(left_wire)
                last_wire = left_wire

            for j, wire in enumerate([first_wire] + left_wires):
                down_wire = Wire(
                    wire.end_point, self.gates[4 * i + j].right_input_position()
                )
                wire.add_output_wire(down_wire)
                down_wire.add_input_wire(wire)
                self.gates[4 * i + j].add_input(down_wire)
                self.add_wire(down_wire)


class CircuitScene(Scene):
    def construct(self):
        circuit = MultiplicationCircuit()
        self.add(circuit)

        circuit.create(self, 30)

        circuit.run_forward(
            self, [True, False, True, True, False, True, False, True], 30
        )

        circuit.reset(self)
        self.wait()

        circuit.run_backward(
            self, [False, False, False, True, True, True, False, True], 30
        )

        return


if __name__ == "__main__":
    scene = CircuitScene()
    scene.render()