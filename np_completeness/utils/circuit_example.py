import numpy as np

from np_completeness.utils.circuit import Circuit
from np_completeness.utils.gate import Gate

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


def make_example_circuit() -> Circuit:
    """Make a simple example circuit with 3 inputs and 2 outputs.

    ALSO USED IN TESTS!
    """
    circuit = Circuit()

    for i, out_value in enumerate([False, True, True]):
        circuit.add_gate(
            f"input_{i}",
            Gate(truth_table={(): (out_value,)}, position=np.array([i, 1, 0])),
        )

    for i in range(2):
        circuit.add_gate(
            f"output_{i}",
            Gate.make_knot(1, 0, np.array([i, -3, 0])),
        )

    circuit.add_gate(
        "and_gate", Gate(truth_table=AND_TABLE, position=np.array([1, 0, 0]))
    )
    circuit.add_gate(
        "or_gate", Gate(truth_table=OR_TABLE, position=np.array([0, -1, 0]))
    )
    circuit.add_gate("knot", Gate.make_knot(1, 2, np.array([1, -2, 0])))

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
    evaluation = circuit.evaluate()
    print(evaluation)
