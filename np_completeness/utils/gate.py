from __future__ import annotations

import itertools
from typing import Literal, TypeAlias

from manim.typing import InternalPoint3D
from pydantic import BaseModel

from np_completeness.utils.util_general import (
    DEFAULT_GATE_LENGTH,
    AnyPoint,
    normalize_position,
)

GateVisualType = Literal[
    "default", "constant", "knot", "invisible", "not", "and", "or", "nand", "+"
]
TruthTable: TypeAlias = dict[tuple[bool, ...], tuple[bool, ...]]


class Gate:
    def __init__(
        self,
        truth_table: TruthTable,
        position: AnyPoint,
        length: float = DEFAULT_GATE_LENGTH,
        visual_type: GateVisualType = "default",
    ):
        """A logical gate, possibly with multiple outputs.

        Args:
            truth_table: A dictionary mapping input values to output values. If we try
                to evaluate for an input combination that's not present in the keys,
                will raise an error.
            position: The position of the gate when visualizing.
            length: How long signal takes to propagate through this gate.
            visual_type: The type of gate to visualize. If "default", will try to infer
                the type from the truth table.
        """
        self.truth_table = truth_table
        check_truth_table(self.truth_table)

        self.position: InternalPoint3D = normalize_position(position)
        self.length = length

        if visual_type == "default":
            visual_type = infer_gate_visual_type(truth_table)

        self.visual_type: GateVisualType = visual_type

    @property
    def n_inputs(self):
        return truth_table_n_inputs(self.truth_table)

    @property
    def n_outputs(self):
        return truth_table_n_outputs(self.truth_table)

    def reverse(self, gate_evaluation: GateEvaluation) -> Gate:
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
            length=self.length,
            visual_type=self.visual_type,
        )

    @staticmethod
    def make_knot(
        position: AnyPoint, n_inputs: int = 1, n_outputs: int = 1, length: float = 0.05
    ):
        if n_inputs == 0:
            # For constants, always output False.
            truth_table = {(): tuple([False] * n_outputs)}
        else:
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
            length=length,
            visual_type="constant" if is_constant else "knot",
        )


def check_truth_table(truth_table: TruthTable):
    entries = list(truth_table.items())

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


def truth_table_n_inputs(truth_table: TruthTable) -> int:
    check_truth_table(truth_table)
    return len(list(truth_table.keys())[0])


def truth_table_n_outputs(truth_table: TruthTable) -> int:
    check_truth_table(truth_table)
    return len(list(truth_table.values())[0])


class GateEvaluation(BaseModel):
    input_values: tuple[bool, ...]
    reach_time: float


NOT_TABLE = {
    (False,): (True,),
    (True,): (False,),
}

AND_TABLE = {
    (False, False): (False,),
    (False, True): (False,),
    (True, False): (False,),
    (True, True): (True,),
}

OR_TABLE = {
    (False, False): (False,),
    (False, True): (True,),
    (True, False): (True,),
    (True, True): (True,),
}

NAND_TABLE = {
    (False, False): (True,),
    (False, True): (True,),
    (True, False): (True,),
    (True, True): (False,),
}


def all_inputs(n_inputs: int) -> list[tuple[bool, ...]]:
    """Return all possible input combinations for `n_inputs`."""
    return list(itertools.product([False, True], repeat=n_inputs))


OR3_TABLE = {inputs: (any(inputs),) for inputs in all_inputs(3)}

# the output is (lower bit, upper bit = carry)
ADD_TABLE = {
    (False, False, False): (False, False),
    (False, False, True): (True, False),
    (False, True, False): (True, False),
    (False, True, True): (False, True),
    (True, False, False): (True, False),
    (True, False, True): (False, True),
    (True, True, False): (False, True),
    (True, True, True): (True, True),
}


def infer_gate_visual_type(
    truth_table: dict[tuple[bool, ...], tuple[bool, ...]],
) -> GateVisualType:
    if truth_table == NOT_TABLE:
        return "not"
    if truth_table == AND_TABLE:
        return "and"
    if truth_table == OR_TABLE:
        return "or"
    if truth_table == NAND_TABLE:
        return "nand"
    if truth_table == ADD_TABLE:
        return "+"

    if (
        truth_table_n_inputs(truth_table) == 0
        or truth_table_n_outputs(truth_table) == 0
    ):
        return "constant"

    return "default"  # unknown
