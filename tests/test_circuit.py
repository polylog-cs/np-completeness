import numpy as np

from np_completeness.utils.circuit import (
    Circuit,
    CircuitEvaluation,
)
from np_completeness.utils.gate import AND_TABLE, OR_TABLE, Gate


def make_circuit_fixture() -> Circuit:
    """Make a simple example circuit with 3 inputs and 2 outputs."""
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
        "knot", Gate.make_knot(np.array([1, -1, 0]), n_inputs=1, n_outputs=2, length=0)
    )

    for i in range(2):
        circuit.add_gate(
            f"output_{i}",
            Gate.make_knot(np.array([i, -3, 0]), n_inputs=1, n_outputs=0, length=0),
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


def test_evaluate():
    circuit = make_circuit_fixture()
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
    circuit = make_circuit_fixture()
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
