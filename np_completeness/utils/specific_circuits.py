import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, np

from np_completeness.utils.circuit import ADD_TABLE, AND_TABLE, OR_TABLE, Circuit
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import (
    GATE_HORIZONTAL_SPACING,
    GATE_VERTICAL_SPACING,
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
    circuit.add_gate("knot", Gate.make_knot(1, 2, np.array([1, -1, 0])))

    for i in range(2):
        circuit.add_gate(
            f"output_{i}",
            Gate.make_knot(1, 0, np.array([i, -3, 0])),
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
    y_start_offset: float,
    x_end_offset: float = 0,
):
    x_start, y_start, _ = circuit.gates[wire_start].position
    x_end, _y_end, _ = circuit.gates[wire_end].position

    circuit.add_wire(
        wire_start,
        wire_end,
        knot_positions=[
            (x_start, y_start + y_start_offset),
            (x_end + x_end_offset, y_start + y_start_offset),
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

            gate_position = circuit.gates[gate_name].position
            input_pos = np.array(
                [
                    gate_position[0] + (0.15 if symbol == "a" else -0.2),
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
            knot_position = circuit.gates[gate_name].position + UP * 0.4 + RIGHT * 0.15
            circuit.add_gate(
                knot_name,
                Gate.make_knot(
                    n_inputs=1,
                    n_outputs=1 if j == (n - 1) else 2,
                    position=knot_position,
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
            knot_position = circuit.gates[gate_name].position + LEFT * 0.2 + UP * 0.3
            circuit.add_gate(
                knot_name,
                Gate.make_knot(
                    n_inputs=1,
                    n_outputs=1 if i == (n - 1) else 2,
                    position=knot_position,
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

        circuit.add_gate(gate_name, Gate.make_knot(1, 0, position))
        from_i = min(i - 1, n - 2)
        # The `min` on this one is just because the last row's adder leads
        # to two outputs.
        from_j = min(i - 1 - from_i, n - 1)

        if i > 0:
            circuit.add_wire(f"plus_{from_i}_{from_j}", gate_name)

    # for n rows, there are n-1 adders, so the first row is special
    for j in range(n):
        add_snake_wire(
            circuit,
            f"and_0_{j}",
            f"plus_0_{j-1}" if j > 0 else "output_0",
            y_start_offset=-0.1 * (j + 1),
        )

    for i in range(1, n):
        for j in range(n):
            add_snake_wire(
                circuit,
                f"and_{i}_{j}",
                f"plus_{i-1}_{j}",
                y_start_offset=-0.2 - 0.1 * j,
                x_end_offset=-0.2,
            )

    # carry wires - note these must be the second and not the first output of
    # the adder, meaning we need to put them here at the end
    for i in range(n - 1):
        for j in range(n - 1):
            circuit.add_wire(
                f"plus_{i}_{j}",
                f"plus_{i}_{j+1}",
                knot_positions=[
                    circuit.gates[f"plus_{i}_{j}"].position + DOWN * 0.2 + LEFT * 0.2,
                    circuit.gates[f"plus_{i}_{j+1}"].position + UP * 0.3 + RIGHT * 0.3,
                ],
            )

    # Some of the adders don't have 3 inputs, add invisible inputs that go to 0
    circuit.add_missing_inputs_and_outputs(visible=False)

    circuit.check()
    return circuit
