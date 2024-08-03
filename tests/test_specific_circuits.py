import pytest

from np_completeness.utils.specific_circuits import (
    MULTIPLICATION_CIRCUIT_SIZE,
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
