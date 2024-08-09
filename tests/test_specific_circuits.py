import pytest

from np_completeness.utils.gate import ADD_TABLE
from np_completeness.utils.specific_circuits import (
    MULTIPLICATION_CIRCUIT_SIZE,
    make_adder_circuit,
    make_multiplication_circuit,
    to_binary,
)


@pytest.mark.parametrize(
    "a,b",
    [
        (0, 0),
        (0, 1),
        (1, 1),
        (3, 1),
        (3, 5),
        (2**MULTIPLICATION_CIRCUIT_SIZE - 1, 1),
        (2**MULTIPLICATION_CIRCUIT_SIZE - 1, 3),
        (2**MULTIPLICATION_CIRCUIT_SIZE - 1, 2**MULTIPLICATION_CIRCUIT_SIZE - 1),
    ],
)
def test_multiplication_circuit(a: int, b: int):
    for cur_a, cur_b in [(a, b), (b, a)]:  # Test commutativity
        circuit = make_multiplication_circuit(to_binary(a), to_binary(b))
        evaluation = circuit.evaluate()

        expected = to_binary(cur_a * cur_b, n_digits=MULTIPLICATION_CIRCUIT_SIZE * 2)
        actual = [
            evaluation.get_gate_inputs(f"output_{i}")[0]
            for i in range(MULTIPLICATION_CIRCUIT_SIZE * 2)
        ]

        assert expected == actual, f"Expected {expected}, got {actual}"


def test_adder_circuit():
    for inputs, (lower_bit, upper_bit) in ADD_TABLE.items():
        circuit = make_adder_circuit(list(inputs))
        evaluation = circuit.evaluate()
        assert (
            evaluation.get_simplified_value("lower_output") == lower_bit
        ), f"Wrong lower bit for {inputs}"
        assert (
            evaluation.get_simplified_value("upper_output") == upper_bit
        ), f"Wrong upper bit for {inputs}"
