from np_completeness.utils.circuit import CircuitEvaluation
from np_completeness.utils.specific_circuits import make_example_circuit


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
        # Outputs have different reach times because of differing wire lengths
        < gate_evaluations["output_1"].reach_time
        < gate_evaluations["output_0"].reach_time
    )


def test_reverse():
    circuit = make_example_circuit()
    circuit = circuit.reverse()
    evaluation: CircuitEvaluation = circuit.evaluate()

    expected = [
        ("input_0", (False,)),
        ("input_1", (True,)),
        ("input_2", (True,)),
        ("and_gate", (True,)),
        ("or_gate", (True,)),
        ("knot", (True, True)),
        ("output_0", ()),
        ("output_1", ()),
    ]

    for gate_name, expected_value in expected:
        assert (
            evaluation.get_gate_inputs(gate_name) == expected_value
        ), f"Gate {gate_name} failed"

    assert evaluation.gate_evaluations["knot"].reach_time == max(
        circuit.get_wire_length("knot", "output_0"),
        circuit.get_wire_length("knot", "output_1"),
    )

    # Reverse back to the original - the gate truth tables are lost
    # because they're not invertible, but the evaluation should still work
    circuit = circuit.reverse()
    evaluation: CircuitEvaluation = circuit.evaluate()

    for gate_name, expected_value in expected:
        # Notice we're checking outputs and not inputs now
        assert (
            evaluation.get_gate_outputs(gate_name) == expected_value
        ), f"Gate {gate_name} failed"
