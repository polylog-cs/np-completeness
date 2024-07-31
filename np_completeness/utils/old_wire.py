from __future__ import annotations

from typing import Any

from manim import *
from manim.typing import InternalPoint3D

from np_completeness.utils.util_general import (
    SIGNAL_SPEED,
    WIRE_COLOR_NONE,
    get_wire_color,
)


class OldWire(VMobject):
    def __init__(self, start: InternalPoint3D, end: InternalPoint3D, **kwargs: Any):
        super().__init__(**kwargs)
        self.start_point: InternalPoint3D = start
        self.end_point: InternalPoint3D = end

        self.value: bool | None = None
        self._future_value: bool | None = None
        self.is_forward = True
        self.input_wire = None
        self.output_wires = []

        self.line = Line(start, end, color=WIRE_COLOR_NONE)
        self.add(self.line)
        self.offset = 1e-6 * (end - start)

        self.activation_animation = False
        self.active = False
        self.activate_progress = ValueTracker(0)
        self.add_updater(self.update_create)

        self.progress = ValueTracker(0)
        self.active_part = Line(start, start + self.offset, color=WIRE_COLOR_NONE)
        self.add(self.active_part)
        self.add_updater(self.update_active_part)

        self.progress_back = ValueTracker(0)
        self.active_part_back = Line(end - self.offset, end, color=WIRE_COLOR_NONE)
        self.add(self.active_part_back)
        self.add_updater(self.update_active_part_back)

    def get_length(self) -> float:
        return np.linalg.norm(self.end_point - self.start_point).astype(float)

    def add_input_wire(self, wire: OldWire):
        self.input_wire = wire

    def add_output_wire(self, wire: OldWire):
        self.output_wires.append(wire)

    def set_value(self, value: bool | None):
        self.value = value
        color = get_wire_color(value)
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

    def update_create(self, mobject: Mobject, dt: float):
        if self.activation_animation:
            if self.active:
                self.activate_progress.set_value(
                    min(
                        self.activate_progress.get_value()
                        + dt * SIGNAL_SPEED / self.get_length(),
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

    def update_active_part(self, mob: Mobject, dt: float):
        if self.is_forward:
            alpha = self.progress.get_value()
            if alpha > 0:
                end = self.line.point_from_proportion(alpha)
                self.active_part.put_start_and_end_on(self.start_point, end)
            if alpha == 1:
                for wire in self.output_wires:
                    if wire.value is None:
                        wire.set_value(self.value)

    def update_active_part_back(self, mob: Mobject, dt: float):
        if not self.is_forward:
            alpha = self.progress_back.get_value()
            if alpha > 0:
                start = self.line.point_from_proportion(1 - alpha)
                self.active_part_back.put_start_and_end_on(start, self.end_point)
            if alpha == 1:
                if self.input_wire is not None and self.input_wire.value is None:
                    self.input_wire.set_value(self.value)

    def propagate_signal(self, dt: float):
        if self.value is not None:
            self.progress.set_value(
                min(
                    self.progress.get_value() + dt * SIGNAL_SPEED / self.get_length(), 1
                )
            )

    def propagate_signal_back(self, dt: float):
        if self.value is not None:
            self.progress_back.set_value(
                min(
                    self.progress_back.get_value()
                    + dt * SIGNAL_SPEED / self.get_length(),
                    1,
                )
            )
