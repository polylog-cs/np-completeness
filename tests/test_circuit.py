from np_completeness.utils.circuit import GateResult
from np_completeness.utils.circuit_example import make_example_circuit


def test_evaluate():
    circuit = make_example_circuit()
    evaluation: dict[str, GateResult] = circuit.evaluate()

    assert evaluation["or_gate"].input_values == (False, True)
    assert evaluation["and_gate"].input_values == (True, True)
    assert evaluation["knot"].input_values == (True,)

    assert (
        0
        == evaluation["input_0"].reach_time
        == evaluation["input_1"].reach_time
        == evaluation["input_2"].reach_time
        < evaluation["and_gate"].reach_time
        < evaluation["or_gate"].reach_time
        < evaluation["knot"].reach_time
    )
