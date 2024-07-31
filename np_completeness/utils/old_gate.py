from typing import Any

from manim import *

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import (
    BASE00,
    BASE1,
    GATE_HEIGHT,
    GATE_TEXT_RATIO,
    GATE_WIDTH,
    SIGNAL_SPEED,
    get_wire_color,
)
from np_completeness.utils.old_wire import OldWire


class OldGate(VMobject):
    def __init__(
        self,
        gate_type: str,
        inputs: list[OldWire] | None = None,
        output: OldWire | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.gate_type = gate_type
        self.inputs = inputs if inputs is not None else []
        self.output = output

        self.rect = Rectangle(
            height=GATE_HEIGHT,
            width=GATE_WIDTH,
            fill_opacity=0.9,
            color=BASE00,
            fill_color=BASE1,
        )
        self.text = (
            Text(gate_type, color=BASE00)
            .move_to(self.rect.get_center())
            .scale_to_fit_height(GATE_HEIGHT * GATE_TEXT_RATIO)
        )

        self.add(self.rect, self.text)

        self.activated = False
        self.activation_animation = False
        self.active = False
        self.activate_progress = ValueTracker(0)
        self.add_updater(self.update_create)

    def update_create(self, mobject: Mobject, dt: float):
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

            alpha = rate_functions.smooth(self.activate_progress.get_value())
            self.rect.scale_to_fit_height(GATE_HEIGHT * alpha + 1e-6)
            self.text.move_to(self.rect.get_center()).scale_to_fit_height(
                self.rect.height * GATE_TEXT_RATIO
            )

    def evaluate(self):
        raise NotImplementedError("Subclasses must implement this method")

    def update_forward(self, dt: float):
        if not self.activated and all(
            input_wire.progress.get_value() == 1 for input_wire in self.inputs
        ):
            self.activated = True
            output_value = self.evaluate()
            self.rect.set_fill(get_wire_color(output_value))
            if self.output:
                self.output.set_value(output_value)

    def update_backward(self, dt: float):
        if (
            not self.activated
            and self.output
            and self.output.progress_back.get_value() >= 0.99
        ):
            self.activated = True
            output_value = self.output.value
            self.rect.set_fill(get_wire_color(output_value))
            for input_wire in self.inputs:
                input_wire.set_value(input_wire._future_value)

    def left_input_position(self):
        return self.rect.get_top() + GATE_WIDTH / 6 * LEFT

    def right_input_position(self):
        return self.rect.get_top() + GATE_WIDTH / 6 * RIGHT


class AndGate(OldGate):
    def __init__(self, **kwargs: Any):
        super().__init__("AND", **kwargs)

    def evaluate(self):
        return all(wire.value for wire in self.inputs)


class OrGate(OldGate):
    def __init__(self, **kwargs: Any):
        super().__init__("OR", **kwargs)

    def evaluate(self):
        return any(wire.value for wire in self.inputs)
