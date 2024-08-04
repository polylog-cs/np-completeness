import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, np

from np_completeness.utils.circuit import (
    ADD_TABLE,
    AND_TABLE,
    NOT_TABLE,
    OR3_TABLE,
    OR_TABLE,
    Circuit,
)
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import (
    GATE_HORIZONTAL_SPACING,
    GATE_VERTICAL_SPACING,
    WIRE_TIGHT_SPACING,
)


def make_example_circuit() -> Circuit:
    """Make a simple example circuit with 3 inputs and 2 outputs.

    ALSO USED IN TESTS!
    """
    circuit = Circuit()

    for i, out_value in enumerate([False, True, True]):
        circuit.add_gate(
            f"input_{i}",
            Gate(
                truth_table={(): (out_value,)},
                position=np.array([i, 3, 0]),
                visual_type="constant",
            ),
        )

    circuit.add_gate(
        "and_gate",
        Gate(truth_table=AND_TABLE, position=np.array([1.5, 1, 0]), visual_type="and"),
    )
    circuit.add_gate(
        "or_gate",
        Gate(truth_table=OR_TABLE, position=np.array([0.5, 0, 0]), visual_type="or"),
    )
    circuit.add_gate(
        "knot", Gate.make_knot(np.array([1, -1, 0]), n_inputs=1, n_outputs=2)
    )

    for i in range(2):
        circuit.add_gate(
            f"output_{i}",
            Gate.make_knot(np.array([i, -3, 0]), n_inputs=1, n_outputs=0),
        )

    circuit.wires = [
        ("input_0", "or_gate"),
        ("input_1", "and_gate"),
        ("input_2", "and_gate"),
        ("and_gate", "or_gate"),
        ("or_gate", "knot"),
        ("knot", "output_0"),
        ("knot", "output_1"),
    ]

    circuit.check()
    return circuit


if __name__ == "__main__":
    circuit = make_example_circuit()
    # evaluation = circuit.evaluate()
    circuit = circuit.reverse()
    evaluation = circuit.evaluate()


def add_snake_wire(
    circuit: Circuit,
    wire_start: str,
    wire_end: str,
    *,
    y_start_offset: float,
    x_end_offset: float = 0,
):
    x_start, y_start, _ = circuit.position_of(wire_start)
    x_end, y_end, _ = circuit.position_of(wire_end)

    assert (
        x_end_offset >= 0
    ), "Expected non-negative offset (will be flipped automatically if needed)"

    x_end_offset = min(x_end_offset, abs(x_start - x_end))
    if x_start < x_end:
        x_end_offset = -x_end_offset

    circuit.add_wire(
        wire_start,
        wire_end,
        knot_positions=[
            (x_start, y_start + y_start_offset),
            (x_end + x_end_offset, y_start + y_start_offset),
            (x_end + x_end_offset, y_end + 0.3),
        ],
    )


MULTIPLICATION_CIRCUIT_SIZE = 4


def to_binary(x: int, n_digits: int = MULTIPLICATION_CIRCUIT_SIZE) -> list[bool]:
    """Convert an integer to a binary list of booleans, least significant bit first.

    Example:
    >>> to_binary(2, n_digits=4)
    [False, True, False, False]
    """
    res = [bool(int(digit)) for digit in bin(x)[2:]][::-1]
    while len(res) < n_digits:
        res.append(False)

    return res


def make_multiplication_circuit(a: list[bool] | int, b: list[bool] | int) -> Circuit:
    circuit = Circuit()
    n = MULTIPLICATION_CIRCUIT_SIZE

    if isinstance(a, int):
        a = to_binary(a, n_digits=n)
    if isinstance(b, int):
        b = to_binary(b, n_digits=n)

    # Define the AND gates with appropriate positions
    for i in range(n):
        for j in range(n):
            gate_name = f"and_{i}_{j}"
            position = (
                2 - 1 * (i + j) * GATE_HORIZONTAL_SPACING - 0.5 * i,
                2 - i * GATE_VERTICAL_SPACING,
            )
            circuit.add_gate(
                gate_name,
                Gate(truth_table=AND_TABLE, position=position, visual_type="and"),
            )

    # Define the input gates and wires
    for t, symbol, values in [(0, "a", a), (1, "b", b)]:
        for j in range(n):
            input_name = f"input_{symbol}_{j}"
            # For visual reasons, the horizontal positioning is different for
            # input A and input B: they're placed under different gates.
            gate_name = f"and_0_{j}" if t == 1 else f"and_{j}_0"

            input_pos = np.array(
                [
                    circuit.x_of(gate_name) + (0.15 if symbol == "a" else -0.2),
                    3.5 - t * 0.5,
                ]
            )
            circuit.add_gate(
                input_name,
                Gate(
                    truth_table={(): (values[j],)},
                    position=input_pos,
                    visual_type="constant",
                ),
            )

    # wires from input A
    for i in range(n):
        for j in range(n):
            knot_name = f"knot_a_{i}_{j}"
            gate_name = f"and_{i}_{j}"
            knot_position = circuit.position_of(gate_name) + UP * 0.4 + RIGHT * 0.15
            circuit.add_gate(
                knot_name,
                Gate.make_knot(
                    knot_position,
                    n_inputs=1,
                    n_outputs=1 if j == (n - 1) else 2,
                ),
            )

            circuit.add_wire(knot_name, gate_name)
            if j == 0:
                circuit.add_wire(f"input_a_{i}", knot_name)
            else:
                circuit.add_wire(f"knot_a_{i}_{j-1}", knot_name)

    # wires from input B
    for i in range(n):
        for j in range(n):
            knot_name = f"knot_b_{i}_{j}"
            gate_name = f"and_{i}_{j}"
            knot_position = circuit.position_of(gate_name) + LEFT * 0.2 + UP * 0.3
            circuit.add_gate(
                knot_name,
                Gate.make_knot(
                    knot_position,
                    n_inputs=1,
                    n_outputs=1 if i == (n - 1) else 2,
                ),
            )

            circuit.add_wire(knot_name, gate_name)
            if i == 0:
                circuit.add_wire(f"input_b_{j}", knot_name)
            else:
                circuit.add_wire(f"knot_b_{i-1}_{j}", knot_name)

    # adder gates
    for i in range(n - 1):
        for j in range(n):
            gate_name = f"plus_{i}_{j}"
            position = (
                (4 - i - j) * GATE_HORIZONTAL_SPACING,
                (0 - i) * GATE_VERTICAL_SPACING,
            )
            circuit.add_gate(
                gate_name,
                Gate(truth_table=ADD_TABLE, position=position, visual_type="+"),
            )

            if i > 0 and j < n - 1:
                circuit.add_wire(f"plus_{i-1}_{j+1}", f"plus_{i}_{j}")

    # outputs
    for i in range(n * 2):
        gate_name = f"output_{i}"
        position = (
            (5 - i) * GATE_HORIZONTAL_SPACING,
            (-3) * GATE_VERTICAL_SPACING,
        )

        circuit.add_gate(gate_name, Gate.make_knot(position, n_inputs=1, n_outputs=0))
        from_i = min(i - 1, n - 2)
        from_j = i - 1 - from_i

        # The first output gets its input without any adders, the last
        # output gets it from the carry of the last adder (wire added later)
        if i > 0 and i < n * 2 - 1:
            circuit.add_wire(f"plus_{from_i}_{from_j}", gate_name)

    # for n rows, there are n-1 adders, so the first row is special
    for j in range(n):
        add_snake_wire(
            circuit,
            f"and_0_{j}",
            f"plus_0_{j-1}" if j > 0 else "output_0",
            y_start_offset=-WIRE_TIGHT_SPACING * (j + 1),
        )

    for i in range(1, n):
        for j in range(n):
            add_snake_wire(
                circuit,
                f"and_{i}_{j}",
                f"plus_{i-1}_{j}",
                y_start_offset=-0.2 - WIRE_TIGHT_SPACING * j,
                x_end_offset=0.2,
            )

    # carry wires - note these must be the second and not the first output of
    # the adder, meaning we need to put them here at the end
    for i in range(n - 1):
        for j in range(n):
            if i == n - 2 and j == n - 1:
                to = f"output_{n*2-1}"
            else:
                to = f"plus_{i}_{j+1}" if j < n - 1 else f"plus_{i+1}_{j}"

            circuit.add_wire(
                f"plus_{i}_{j}",
                to,
                knot_positions=[
                    circuit.position_of(f"plus_{i}_{j}") + DOWN * 0.2 + LEFT * 0.2,
                    circuit.position_of(f"plus_{i}_{j}")
                    + UP * 0.3
                    + RIGHT * (0.3 - GATE_HORIZONTAL_SPACING),
                ],
            )

    # Some of the adders don't have 3 inputs, add invisible inputs that go to 0
    circuit.add_missing_inputs_and_outputs(visible=False)

    circuit.check()
    return circuit


def _make_xor_gadget(circuit: Circuit, prefix: str, input_0: str, input_1: str) -> str:
    """Make a XOR gadget out of NOT, AND and OR gates and return the name of the output."""
    input_x_0, input_y_0, _ = circuit.position_of(input_0)
    input_x_1, input_y_1, _ = circuit.position_of(input_1)

    # In other places, we use right-to-left indexing, so let's be consistent
    assert input_x_0 > input_x_1
    # Start from the lower of the two positions
    input_y = min(input_y_0, input_y_1)

    for i, (input_x, input_name) in enumerate(
        [(input_x_0, input_0), (input_x_1, input_1)]
    ):
        knot_name = circuit.add_gate(
            f"{prefix}_knot_{i}",
            Gate.make_knot(
                (input_x, input_y - GATE_VERTICAL_SPACING * 0.5),
                n_inputs=1,
                n_outputs=2,
            ),
        )
        circuit.add_wire(input_name, knot_name)

        not_name = circuit.add_gate(
            f"{prefix}_not_{i}",
            Gate(
                truth_table=NOT_TABLE,
                position=circuit.position_of(knot_name)
                + np.array(
                    [
                        GATE_HORIZONTAL_SPACING * 0.5 * (-1 if i == 0 else 1),
                        -GATE_VERTICAL_SPACING / 2,
                        0,
                    ]
                ),
                visual_type="not",
            ),
        )
        knot2_name = circuit.add_gate(
            f"{prefix}_knot_{i}'",
            Gate.make_knot(
                (
                    circuit.x_of(not_name),
                    circuit.y_of(knot_name),
                ),
            ),
        )
        circuit.add_wire(knot_name, knot2_name)
        circuit.add_wire(knot2_name, not_name)

        circuit.add_gate(
            f"{prefix}_and_{i}",
            Gate(
                truth_table=AND_TABLE,
                position=circuit.position_of(knot_name) + DOWN * GATE_VERTICAL_SPACING,
                visual_type="and",
            ),
        )
        circuit.add_wire(knot_name, f"{prefix}_and_{i}")

    for i in range(2):
        not_name = f"{prefix}_not_{i}"
        knot = circuit.add_knot(position=circuit.position_of(not_name) + DOWN * 0.2)
        circuit.add_wire(not_name, knot)
        circuit.add_wire(knot, f"{prefix}_and_{1-i}")

    or_name = circuit.add_gate(
        f"{prefix}_or",
        Gate(
            OR_TABLE,
            (
                (input_x_0 + input_x_1) / 2,
                circuit.y_of(f"{prefix}_and_0") - GATE_VERTICAL_SPACING * 0.5,
            ),
            visual_type="or",
        ),
    )
    circuit.add_wire(f"{prefix}_and_0", or_name)
    circuit.add_wire(f"{prefix}_and_1", or_name)

    return or_name


def make_adder_circuit(inputs: list[bool]) -> Circuit:
    circuit = Circuit()

    for i in range(3):
        circuit.add_gate(
            f"input_{i}",
            Gate(
                truth_table={(): (inputs[i],)},
                position=(-GATE_HORIZONTAL_SPACING * i, GATE_VERTICAL_SPACING * 3.5),
                visual_type="constant",
            ),
        )

    # Majority AND gates + knots for their inputs
    for i in range(3):
        name = f"maj_and_{i}"
        circuit.add_gate(
            name,
            Gate(
                truth_table=AND_TABLE,
                position=(
                    -GATE_HORIZONTAL_SPACING * (i + 1),
                    GATE_VERTICAL_SPACING * 1.5,
                ),
                visual_type="and",
            ),
        )
        for j in range(2):
            knot_name = f"maj_and_knot_{i}_{j}"
            circuit.add_gate(
                knot_name,
                Gate.make_knot(
                    circuit.position_of(name)
                    + np.array(
                        [
                            0.2 * (0.5 - j),
                            0.3,
                            0,
                        ]
                    ),
                ),
            )
            circuit.add_wire(knot_name, name)

    # Wires from the inputs to the AND gates
    for i, (output_knot1, output_knot2) in enumerate(
        [
            ["maj_and_knot_0_0", "maj_and_knot_1_0"],
            ["maj_and_knot_0_1", "maj_and_knot_2_0"],
            ["maj_and_knot_1_1", "maj_and_knot_2_1"],
        ]
    ):
        knot_x = [
            circuit.x_of(f"input_{i}"),
            circuit.x_of(output_knot1),
            circuit.x_of(output_knot2),
            circuit.x_of(f"input_{i}") + GATE_HORIZONTAL_SPACING * (4 - i * 0.5),
        ]
        knot_y = (
            circuit.y_of(f"input_{i}") - GATE_VERTICAL_SPACING + WIRE_TIGHT_SPACING * i
        )
        k1 = circuit.add_knot(
            (knot_x[0], knot_y), n_inputs=1, n_outputs=2, name=f"input_{i}_knot"
        )
        k2 = circuit.add_knot((knot_x[1], knot_y), n_inputs=1, n_outputs=2)
        k3 = circuit.add_knot((knot_x[2], knot_y), n_inputs=1, n_outputs=1)
        k4 = circuit.add_knot(
            (knot_x[3], knot_y), n_inputs=1, n_outputs=1, name=f"xor3_input_{i}"
        )

        circuit.wires.extend(
            [
                (f"input_{i}", k1),
                (k1, k2),
                (k2, output_knot1),
                (k2, k3),
                (k3, output_knot2),
                (k1, k4),
            ]
        )

    # ORing the three together to get the carry
    name = "maj_or3"
    circuit.add_gate(
        name,
        Gate(
            truth_table=OR3_TABLE,
            position=circuit.position_of("maj_and_1") + DOWN * GATE_VERTICAL_SPACING,
            visual_type="or",
        ),
    )
    for i in range(3):
        add_snake_wire(
            circuit,
            f"maj_and_{i}",
            "maj_or3",
            y_start_offset=-0.3,
            x_end_offset=WIRE_TIGHT_SPACING,
        )

    # XORing three numbers via two XOR gadgets
    xor_output_0 = _make_xor_gadget(
        circuit, prefix="xor0", input_0="xor3_input_1", input_1="xor3_input_2"
    )
    xor_output_1 = _make_xor_gadget(
        circuit, prefix="xor1", input_0="xor3_input_0", input_1=xor_output_0
    )

    lower_output = circuit.add_knot(
        position=circuit.position_of(xor_output_1) + DOWN * GATE_VERTICAL_SPACING,
        name="lower_output",
        n_inputs=1,
        n_outputs=0,
    )
    circuit.add_wire(xor_output_1, lower_output)

    # The upper output bit also happens to be the upper one on the screen hehe
    upper_output = circuit.add_knot(
        position=circuit.position_of("maj_or3") + DOWN * GATE_VERTICAL_SPACING,
        name="upper_output",
        n_inputs=1,
        n_outputs=0,
    )
    circuit.add_wire("maj_or3", upper_output)

    return circuit
