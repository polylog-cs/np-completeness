from __future__ import annotations

from typing import Literal

import numpy as np
from manim.typing import InternalPoint3D, Point2D, Point3D
from pydantic import BaseModel

from np_completeness.utils.util_general import DEFAULT_GATE_LENGTH

GateVisualType = Literal["default", "constant", "knot", "and", "or"]


class Gate:
    def __init__(
        self,
        truth_table: dict[tuple[bool, ...], tuple[bool, ...]],
        position: Point3D | Point2D,
        length: float = DEFAULT_GATE_LENGTH,
        visual_type: GateVisualType = "default",
    ):
        self.truth_table = truth_table
        self.check_truth_table()

        self.position: InternalPoint3D = normalize_position(position)
        self.length = length
        self.visual_type = visual_type

    def check_truth_table(self):
        entries = list(self.truth_table.items())

        if not entries:
            raise ValueError(
                "Truth table is empty. For gates with no inputs or no outputs, "
                "add an entry with an empty tuple () as the key (no inputs) "
                "or value (no outputs)."
            )

        some_inputs, some_outputs = entries[0]

        for inputs, outputs in entries:
            if len(inputs) != len(some_inputs):
                raise ValueError(
                    f"Invalid truth table: {inputs} has {len(inputs)} inputs, "
                    f"expected {len(some_inputs)}"
                )

            if len(outputs) != len(some_outputs):
                raise ValueError(
                    f"Invalid truth table: {outputs} has {len(outputs)} outputs, "
                    f"expected {len(some_outputs)}"
                )

    @property
    def n_inputs(self):
        self.check_truth_table()
        return len(list(self.truth_table.keys())[0])

    @property
    def n_outputs(self):
        self.check_truth_table()
        return len(list(self.truth_table.values())[0])

    def invert(self, gate_evaluation: GateEvaluation) -> Gate:
        input_values = gate_evaluation.input_values
        output_values = self.truth_table[input_values]

        return Gate(
            # The only supported input value for the inverted gate
            # is the actual output value that we got. This is because
            # gates will usually be non-invertible - for example, if
            # we have an AND gate that had False as the output, we don't
            # know what the inputs were (which is why running circuits
            # backwards is hard).
            truth_table={output_values: input_values},
            position=self.position.copy(),
        )

    @staticmethod
    def make_knot(n_inputs: int, n_outputs: int, position: InternalPoint3D):
        # A mix of True and False values is not supported.
        truth_table = {
            tuple([False] * n_inputs): tuple([False] * n_outputs),
            tuple([True] * n_inputs): tuple([True] * n_outputs),
        }

        # No inputs or no outputs means it's a constant at the beginning or end
        # of the graph
        is_constant = n_inputs == 0 or n_outputs == 0

        return Gate(
            truth_table,
            position,
            length=0,
            visual_type="constant" if is_constant else "knot",
        )


class GateEvaluation(BaseModel):
    input_values: tuple[bool, ...]
    reach_time: float


def normalize_position(
    position: Point3D | Point2D,
) -> InternalPoint3D:
    if isinstance(position, tuple):
        if len(position) == 2:
            position = np.array([*position, 0])
        elif len(position) == 3:
            position = np.array(position)
        else:
            raise ValueError(f"Invalid position: {position}")
    else:
        if position.shape == (2,):
            position = np.array([*position, 0])
        elif position.shape == (3,):
            pass
        else:
            raise ValueError(f"Invalid position: {position}")

    return position.astype(np.float64)
