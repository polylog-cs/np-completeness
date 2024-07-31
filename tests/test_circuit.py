from np_completeness.utils.circuit import CircuitEvaluation
from np_completeness.utils.circuit_example import make_example_circuit


def test_evaluate():
    circuit = make_example_circuit()
    evaluation: CircuitEvaluation = circuit.evaluate()

    gate_evaluations = evaluation.gate_evaluations

    assert gate_evaluations["or_gate"].input_values == (False, True)
    assert gate_evaluations["and_gate"].input_values == (True, True)
    assert gate_evaluations["knot"].input_values == (True,)

    assert (
        0
        == gate_evaluations["input_0"].reach_time
        == gate_evaluations["input_1"].reach_time
        == gate_evaluations["input_2"].reach_time
        < gate_evaluations["and_gate"].reach_time
        < gate_evaluations["or_gate"].reach_time
        < gate_evaluations["knot"].reach_time
    )
