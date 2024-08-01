from manim import *

# Imported for the side effect of changing the default colors
from np_completeness.utils.circuit import Circuit
from np_completeness.utils.circuit_example import AND_TABLE, make_example_circuit
from np_completeness.utils.gate import Gate
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.util_general import (
    GATE_HORIZONTAL_SPACING,
    GATE_VERTICAL_SPACING,
)


def make_multiplication_circuit(a: list[bool], b: list[bool]) -> Circuit:
    circuit = Circuit()
    n = 4

    # Define the AND gates with appropriate positions
    for i in range(n):
        for j in range(n):
            gate_name = f"and_gate_{i}_{j}"
            position = (
                (i + j) * GATE_HORIZONTAL_SPACING * LEFT
                + i * GATE_VERTICAL_SPACING * DOWN
                + 0.5 * i * LEFT
                + 2 * UP
                + 4 * RIGHT
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
            gate_name = f"and_gate_0_{j}" if t == 1 else f"and_gate_{j}_0"

            gate_position = circuit.gates[gate_name].position
            input_pos = np.array(
                [
                    gate_position[0] + (0.15 if symbol == "a" else -0.35),
                    4 - t,
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
            gate_name = f"and_gate_{i}_{j}"
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
            gate_name = f"and_gate_{i}_{j}"
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

    circuit.check()
    return circuit


class CircuitScene(Scene):
    def construct(self):
        circuit = make_multiplication_circuit(
            a=[True, False, True, True], b=[False, True, False, True]
        )
        circuit.add_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True)
        # manim_circuit.shift(DOWN)
        self.add(manim_circuit)

        self.play(manim_circuit.animate_evaluation())
        self.wait()


class ExampleCircuitScene(Scene):
    def construct(self):
        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit)
        self.add(manim_circuit)
        self.wait()

        self.play(manim_circuit.animate_evaluation())

        self.wait(1)

        circuit = make_example_circuit()
        reversed_manim_circuit = ManimCircuit(circuit.reverse())

        # We can add a crossfade in post, no need to do it in Manim.
        self.clear()
        self.wait(1)
        self.add(reversed_manim_circuit)

        self.play(reversed_manim_circuit.animate_evaluation(reversed=True))
        self.wait(2)


if __name__ == "__main__":
    circuit = make_multiplication_circuit(
        a=[True, False, True, True], b=[False, True, False, True]
    )
    circuit.display_graph(with_evaluation=False)
