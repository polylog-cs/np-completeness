from typing import Any

from manim import *
from manim.typing import InternalPoint3D

from np_completeness.utils.circuit import Circuit
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import (
    BASE00,
    BASE2,
    GATE_HEIGHT,
    GATE_TEXT_RATIO,
    GATE_WIDTH,
    WIRE_WIDTH,
    get_wire_color,
)


class ManimGate(VMobject):
    def __init__(self, gate: Gate, value: bool | None = None):
        super().__init__()
        self.gate = gate

        fill_color = get_wire_color(value)

        if gate.visual_type == "knot":
            pass  # A knot is not shown at all
        elif gate.visual_type == "constant":
            self.circle = Circle(
                radius=GATE_HEIGHT / 2,
                color=BASE00,
                fill_color=fill_color,
                fill_opacity=0.9,
            )
            self.circle.move_to(gate.position)

            self.add(self.circle)
        else:
            self.rect = Rectangle(
                height=GATE_HEIGHT,
                width=GATE_WIDTH,
                fill_opacity=0.9,
                color=BASE00,
                fill_color=fill_color,
            )
            self.rect.move_to(gate.position)

            text = "?" if gate.visual_type == "default" else gate.visual_type.upper()

            self.text = (
                Text(text, color=BASE2)
                .move_to(self.rect.get_center())
                .scale_to_fit_height(GATE_HEIGHT * GATE_TEXT_RATIO)
            )

            self.add(self.rect, self.text)

    def animate_to_value(self, value: bool | None) -> Animation:
        new_gate = ManimGate(self.gate, value)
        return self.animate.become(new_gate)


class ManimWire(VMobject):
    def __init__(
        self,
        start: InternalPoint3D,
        end: InternalPoint3D,
        value: bool,
        progress: float = 0,
    ):
        super().__init__()
        self.start_point: InternalPoint3D = start
        self.end_point: InternalPoint3D = end
        self.value = value
        self.progress = progress

        self.background_line = Line(
            start, end, color=get_wire_color(None), stroke_width=WIRE_WIDTH
        )
        self.value_line = Line(
            start,
            interpolate(start, end, progress),
            color=get_wire_color(value),
            stroke_width=WIRE_WIDTH,
        )

        self.add(self.background_line, self.value_line)

    def set_progress(self, progress: float):
        new_wire = ManimWire(self.start_point, self.end_point, self.value, progress)
        self.become(new_wire)


class FillWire(Animation):
    def __init__(self, wire: ManimWire, **kwargs: Any) -> None:  # type: ignore[reportInconsistentConstructor]
        super().__init__(wire, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        assert isinstance(self.mobject, ManimWire)
        self.mobject.set_progress(alpha)


class ManimCircuit(VGroup):
    def __init__(self, circuit: Circuit):
        super().__init__()
        self.circuit = circuit
        evaluation = circuit.evaluate()

        self.gates = {
            name: ManimGate(gate) for name, gate in self.circuit.gates.items()
        }
        self.wires = {
            (wire_start, wire_end): ManimWire(
                self.circuit.gates[wire_start].position,
                self.circuit.gates[wire_end].position,
                evaluation.get_wire_value(wire_start, wire_end),
            )
            for wire_start, wire_end in self.circuit.wires
        }

        # Add wires first so they are behind the gates
        self.add(*self.wires.values(), *self.gates.values())

    def animate_evaluation(self, reversed: bool = False) -> AnimationGroup:
        evaluation = self.circuit.evaluate()
        animations = []

        MIN_DURATION = 0.01  # Prevent divison by 0

        for (wire_start, wire_end), manim_wire in self.wires.items():
            start_time = (
                evaluation.gate_evaluations[wire_start].reach_time
                + self.circuit.gates[wire_start].length
            )
            duration = max(
                self.circuit.get_wire_length(wire_start, wire_end), MIN_DURATION
            )

            # A complicated Manim construction that says "wait for start_time seconds,
            # start filling the wire and end at end_time seconds"
            animations.append(
                AnimationGroup(
                    *[
                        Wait(start_time),
                        FillWire(manim_wire, run_time=duration),
                    ],
                    lag_ratio=1.0,
                    run_time=start_time + duration,
                )
            )

        for gate_name, manim_gate in self.gates.items():
            gate_evaluation = evaluation.gate_evaluations[gate_name]
            start_time = gate_evaluation.reach_time
            duration = max(self.circuit.gates[gate_name].length, MIN_DURATION)

            animations.append(
                AnimationGroup(
                    *[
                        Wait(start_time),
                        manim_gate.animate_to_value(
                            evaluation.get_simplified_value(
                                gate_name, reversed=reversed
                            )
                        ),
                    ],
                    lag_ratio=1.0,
                    run_time=start_time + duration,
                )
            )

        # These all get played "simultaneously" but there are delays internal to the
        # individual animations
        return AnimationGroup(*animations)
