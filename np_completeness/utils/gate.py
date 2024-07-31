import numpy as np
from manim.typing import InternalPoint3D, Point2D, Point3D


class Gate:
    def __init__(
        self,
        truth_table: dict[tuple[bool, ...], tuple[bool, ...]],
        position: Point3D | Point2D,
        length: float = 1,
    ):
        self.truth_table = truth_table
        self.check_truth_table()

        self.position: InternalPoint3D = normalize_position(position)
        self.length = length

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

    @staticmethod
    def make_knot(n_inputs: int, n_outputs: int, position: InternalPoint3D):
        # A mix of True and False values is not supported.
        truth_table = {
            tuple([False] * n_inputs): tuple([False] * n_outputs),
            tuple([True] * n_inputs): tuple([True] * n_outputs),
        }
        return Gate(truth_table, position, length=0)


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
