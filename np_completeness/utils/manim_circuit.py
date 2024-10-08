from pathlib import Path
from typing import Any

from manim import *
from manim.typing import InternalPoint3D

from np_completeness.utils.circuit import Circuit
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import (
    BASE01,
    BASE2,
    GATE_HEIGHT,
    GATE_TEXT_RATIO,
    GATE_WIDTH,
    WIRE_WIDTH,
    get_wire_color,
)


class ManimGate(VMobject):
    def __init__(
        self,
        gate: Gate,
        value: bool | None = None,
        scale: float = 1,
        wire_scale: float = 1,
    ):
        super().__init__()
        self.gate = gate

        fill_color = get_wire_color(value)
        self._scale = scale  # don't conflict with the `scale()` method

        if gate.visual_type == "invisible":
            pass
        elif gate.visual_type == "knot":
            self.circle = Dot(
                radius=0.026 * wire_scale,
                color=fill_color,
            )
            self.circle.move_to(gate.position)

            self.add(self.circle)
        elif gate.visual_type == "constant":
            self.circle = Dot(
                radius=GATE_HEIGHT * 0.3 * scale,
                color=fill_color,
            )
            self.circle.move_to(gate.position)

            self.add(self.circle)
        else:
            self.rect = Rectangle(
                height=GATE_HEIGHT * scale,
                width=GATE_WIDTH * scale,
                fill_opacity=1.0,
                color=BASE01,
                stroke_opacity=0,
                fill_color=fill_color,
            )
            self.rect.move_to(gate.position)

            text = "?" if gate.visual_type == "default" else gate.visual_type.upper()

            self.text = (
                Text(text, color=BASE2)
                .move_to(self.rect.get_center())
                .scale_to_fit_height(GATE_HEIGHT * GATE_TEXT_RATIO * scale)
            )

            self.add(self.rect, self.text)

    def set_value(self, value: bool | None):
        """Set the value of this gate. Helper for animate_to_value()."""
        for mobject in self.submobjects:
            if not isinstance(mobject, Text):
                mobject.set_fill(get_wire_color(value))

    def animate_to_value(self, value: bool | None, **kwargs: Any) -> Animation:
        """Animate the setting of the value of this gate."""
        # ignore typing because of weird type annotation for self.animate
        return self.animate(**kwargs).set_value(value)  # type: ignore


class ManimWire(VMobject):
    def __init__(
        self,
        start: InternalPoint3D,
        end: InternalPoint3D,
        value: bool,
        progress: float = 0,
        scale: float = 1,
    ):
        super().__init__()
        self.start_point: InternalPoint3D = start
        self.end_point: InternalPoint3D = end
        self.value = value
        self.progress = progress
        self._scale = scale  # don't conflict with the `scale()` method

        self.background_line = Line(
            start, end, color=get_wire_color(None), stroke_width=WIRE_WIDTH * scale
        )
        progress_end = interpolate(start, end, max(progress, 0.00001))
        self.value_line = Line(
            start,
            progress_end,
            color=get_wire_color(value),
            stroke_width=WIRE_WIDTH * scale,
        )

        self.add(self.background_line, self.value_line)

    def set_progress(self, progress: float):
        start = self.background_line.get_all_points()[0]
        end = self.background_line.get_all_points()[-1]
        if not np.array_equal(start, end):
            self.value_line.put_start_and_end_on(
                start, interpolate(start, end, max(progress, 0.00001))
            )


class FillWire(Animation):
    def __init__(self, wire: ManimWire, **kwargs: Any) -> None:  # type: ignore[reportInconsistentConstructor]
        super().__init__(wire, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        assert isinstance(self.mobject, ManimWire)
        self.mobject.set_progress(alpha)


class ManimCircuit(VGroup):
    def __init__(
        self,
        circuit: Circuit,
        scale: float = 1,
        with_evaluation: bool = True,
        wire_scale: float | None = None,
    ):
        """A Manim representation of a circuit.

        Args:
            circuit: The circuit to visualize.
            scale: The scale of the circuit. This doesn't scale the positions, just the
                size of the gates and wires.
            with_evaluation: Whether to evaluate the circuit to be able to show the
                progress of the evaluation. (We could probably do this lazily only when
                we need to and not in the constructor.)
        """
        super().__init__()
        self.circuit = circuit

        if with_evaluation:
            evaluation = circuit.evaluate()
        else:
            evaluation = None

        if wire_scale is None:
            wire_scale = scale
        self.gates = {
            name: ManimGate(gate, scale=scale, wire_scale=wire_scale)
            for name, gate in self.circuit.gates.items()
        }
        self.wires = {
            (wire_start, wire_end): ManimWire(
                self.circuit.gates[wire_start].position,
                self.circuit.gates[wire_end].position,
                evaluation.get_wire_value(wire_start, wire_end)
                if evaluation
                else False,
                scale=wire_scale,
            )
            for wire_start, wire_end in self.circuit.wires
        }

        # TODO(vv): some knots appear before AND gates and this `bg_gates` doesn't
        #   seem to help. Why?
        bg_gates = ["knot", "invisible"]
        self.add(
            # Add wires first so they are behind the gates
            *self.wires.values(),
            *[g for g in self.gates.values() if g.gate.visual_type in bg_gates],
            *[g for g in self.gates.values() if g.gate.visual_type not in bg_gates],
        )

    def animate_inputs(self) -> AnimationGroup:
        """Animate the input nodes filling with their given color."""
        anims = []
        for manim_gate in self.gates.values():
            if manim_gate.gate.n_inputs == 0:
                value = manim_gate.gate.truth_table[()][0]
                anims.append(manim_gate.animate_to_value(value))

        return LaggedStart(*anims)

    def animate_evaluation(
        self,
        scene: Scene,  # Hack: we need the scene in order to play sounds.
        reversed: bool = False,
        speed: float = 1,
    ) -> AnimationGroup:
        """Animate the color flowing through the wires to evaluate the circuit."""
        evaluation = self.circuit.evaluate()
        animations = []

        speed *= 3  # make it faster while keeping the default speed at 0
        MIN_DURATION = 0.01  # Prevent divison by 0
        rng = np.random.default_rng(37)  # for sounds jitter

        for (wire_start, wire_end), manim_wire in self.wires.items():
            start_time = (
                evaluation.gate_evaluations[wire_start].reach_time
                + self.circuit.gates[wire_start].length
            ) / speed
            duration = (
                max(self.circuit.get_wire_length(wire_start, wire_end), MIN_DURATION)
                / speed
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
            gate = self.circuit.gates[gate_name]
            gate_evaluation = evaluation.gate_evaluations[gate_name]

            start_time = gate_evaluation.reach_time
            start_time = max(0, start_time + rng.normal(scale=0.1, loc=0.05))
            start_time /= speed

            duration = max(gate.length, MIN_DURATION) / speed

            simplified_value = evaluation.get_simplified_value(
                gate_name, reversed=reversed
            )

            # Jitter the start time for cases where there's a lot of gates going
            # off at the same time

            animations.append(
                AnimationGroup(
                    *[
                        Wait(start_time),
                        manim_gate.animate_to_value(
                            simplified_value,
                            run_time=duration,
                        ),
                    ],
                    lag_ratio=1.0,
                    run_time=start_time + duration,
                )
            )
            if simplified_value is not None:
                add_sound_for_gate(
                    scene,
                    manim_gate,
                    simplified_value,
                    start_time,
                )

        # These all get played "simultaneously" but there are delays internal to the
        # individual animations
        return AnimationGroup(*animations)

    def set_stroke_width(self, scale: float):
        for wire in self.wires.values():
            wire.background_line.set_stroke_width(scale * WIRE_WIDTH)
            wire.value_line.set_stroke_width(scale * WIRE_WIDTH)


def add_sound_for_gate(
    scene: Scene, manim_gate: ManimGate, value: bool, time_offset: float
):
    gate = manim_gate.gate
    if gate.visual_type in ["knot", "invisible"] or gate.n_inputs == 0:
        return  # No sound for "utility gates" and inputs

    if gate.n_outputs == 0:
        sound_file = "click_2" if value else "click_1"
    else:
        sound_file = "click_0" if value else "click_3"

    scene.add_sound(
        str(Path(__file__).parents[1] / f"audio/click/{sound_file}.wav"),
        time_offset=time_offset,
        gain=-12.0,
    )
