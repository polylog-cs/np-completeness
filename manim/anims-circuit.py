from manim import *

GATE_WIDTH = 1.5
GATE_HEIGHT = 1
SIGNAL_SPEED = 0.5  # units per second
WIRE_COLOR = WHITE

class Wire(VMobject):
    def __init__(self, start, end, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start
        self.end_point = end
        self.value = None
        self.future_value = None
        self.is_forward = True # this should not be necessary but ...

        self.line = Line(start, end, color = WIRE_COLOR)
        self.add(self.line)
        self.offset = 1e-6 * (end - start)
        

        self.progress = ValueTracker(0)
        self.active_part = Line(start, start + self.offset, color=WIRE_COLOR)
        self.add(self.active_part)        
        self.add_updater(self.update_active_part)

        self.progress_back = ValueTracker(0)
        self.active_part_back = Line(end - self.offset, end, color=WIRE_COLOR)
        self.add(self.active_part_back)        
        self.add_updater(self.update_active_part_back)

    def set_value(self, value):
        self.value = value
        color = RED if value else BLUE
        self.active_part.set_color(color)
        self.active_part_back.set_color(color)
        self.progress.set_value(0)
        self.progress_back.set_value(0)
        self.active_part.put_start_and_end_on(self.start_point, self.start_point+self.offset)
        self.active_part_back.put_start_and_end_on(self.end_point-self.offset, self.end_point)


    def update_active_part(self, mob, dt):
        if self.is_forward:
            alpha = self.progress.get_value()
            if alpha > 0:
                end = self.line.point_from_proportion(alpha)
                self.active_part.put_start_and_end_on(self.start_point+0.1*UP, end)
        
    def update_active_part_back(self, mob, dt):
        if not self.is_forward:
            alpha = self.progress_back.get_value()
            print(alpha)
            if alpha > 0:
                start = self.line.point_from_proportion(1-alpha)
                self.active_part_back.put_start_and_end_on(start+0.1*DOWN, self.end_point)

    def propagate_signal(self, dt):
        if self.value is not None:
            self.progress.set_value(min(self.progress.get_value() + dt * SIGNAL_SPEED, 1))

    def propagate_signal_back(self, dt):
        if self.value is not None:
            self.progress_back.set_value(min(self.progress_back.get_value() + dt * SIGNAL_SPEED, 1))

class Gate(Rectangle):
    def __init__(self, gate_type, inputs=None, output=None, **kwargs):
        super().__init__(height=GATE_HEIGHT, width=GATE_WIDTH, fill_opacity=0.5, **kwargs)
        self.gate_type = gate_type
        self.inputs = inputs if inputs is not None else []
        self.output = output
        self.text = Text(gate_type).move_to(self.get_center())
        self.add(self.text)
        self.activated = False

    def add_input(self, wire):
        self.inputs.append(wire)

    def set_output(self, wire):
        self.output = wire

    def evaluate(self):
        raise NotImplementedError("Subclasses must implement this method")

    def activate(self, dt):
        if not self.activated and all(input_wire.progress.get_value() == 1 for input_wire in self.inputs):
            self.activated = True
            output_value = self.evaluate()
            self.set_fill(RED if output_value else BLUE)
            if self.output:
                self.output.set_value(output_value)

    def activate_back(self, dt):
        if not self.activated and self.output and self.output.progress_back.get_value() >= 0.99:
            self.activated = True
            output_value = self.output.value
            self.set_fill(RED if output_value else BLUE)
            for input_wire in self.inputs:
                input_wire.set_value(input_wire.future_value)

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

    def run_forward(self, scene, inputs, duration=10):
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

        self._remove_updaters(scene)

    def run_backward(self, scene, inputs, duration=10):

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

        self._remove_updaters(scene)

    def _run_forward_internal(self, inputs):
        for wire in self.wires:
            wire.future_value = None # variable is used only internally
        
        # Set input values
        for wire, value in zip(self.input_wires, inputs):
            wire.future_value = value

        # Keep track of gates that have been evaluated
        evaluated_gates = set()

        while len(evaluated_gates) < len(self.gates):
            for gate in self.gates:
                if gate not in evaluated_gates and all(input_wire.future_value is not None for input_wire in gate.inputs):
                    output_value = gate.evaluate()
                    if gate.output:
                        gate.output.future_value = output_value
                    evaluated_gates.add(gate)



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

        #first set the length to 0 and only then remove the updaters

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

    # def reset(self, scene):
    #     anims = []
    #     for wire in self.wires:
    #         anims.append(wire.active_part.animate.put_start_and_end_on(wire.start_point, wire.start_point+wire.offset))
    #         anims.append(wire.active_part_back.animate.put_start_and_end_on(wire.end_point-wire.offset, wire.end_point))
    #     for gate in self.gates:
    #         anims.append(gate.animate.set_fill(WIRE_COLOR))
    #     scene.play(*anims)

    #     for wire in self.wires:
    #         wire.progress.set_value(0)
    #         wire.progress_back.set_value(0)
    #         wire.value = None
    #         wire.future_value = None
    #         scene.remove_updater(wire.propagate_signal)
    #         scene.remove_updater(wire.propagate_signal_back)

    #     for gate in self.gates:
    #         gate.activated = False
    #         scene.remove_updater(gate.activate)
    #         scene.remove_updater(gate.activate_back)

    #     scene.wait(0.1)

class CircuitScene(Scene):
    def construct(self):
        circuit = Circuit()

        and_gate = AndGate()
        or_gate = OrGate()

        and_gate.move_to(LEFT * 2)
        or_gate.move_to(RIGHT * 2)

        input_wire1 = Wire(and_gate.get_top() + GATE_WIDTH/6*LEFT + GATE_HEIGHT*UP, 
                           and_gate.get_top() + GATE_WIDTH/6*LEFT)
        input_wire2 = Wire(and_gate.get_top() + GATE_WIDTH/6*RIGHT + GATE_HEIGHT*UP, 
                           and_gate.get_top() + GATE_WIDTH/6*RIGHT)
        middle_wire = Wire(and_gate.get_right(), or_gate.get_left())
        input_wire3 = Wire(or_gate.get_top() + GATE_HEIGHT*UP, or_gate.get_top())
        output_wire = Wire(or_gate.get_bottom(), or_gate.get_bottom() + GATE_HEIGHT*DOWN)

        and_gate.add_input(input_wire1)
        and_gate.add_input(input_wire2)
        and_gate.set_output(middle_wire)

        or_gate.add_input(middle_wire)
        or_gate.add_input(input_wire3)
        or_gate.set_output(output_wire)

        circuit.add_gate(and_gate)
        circuit.add_gate(or_gate)
        circuit.add_input_wire(input_wire1)
        circuit.add_input_wire(input_wire2)
        circuit.add_input_wire(input_wire3)
        circuit.add_wire(middle_wire)
        circuit.add_output_wire(output_wire)

        self.add(circuit)

        circuit.run_forward(self, [True, False, True], 10)
        self.wait()

        circuit.reset(self)
        self.wait()


        circuit.run_backward(self, [True, False, True], 10)
        self.wait()

        # # circuit.reset(self)
        # # self.wait()

        # circuit.run_forward(self, [True, True, True], 10)
        # self.wait()

        return



        self.wait(1)

if __name__ == "__main__":
    scene = CircuitScene()
    scene.render()