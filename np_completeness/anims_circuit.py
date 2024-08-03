from manim import *

from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import (
    make_example_circuit,
    make_multiplication_circuit,
)

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import (
    disable_rich_logging,
)


class CircuitScene(Scene):
    def construct(self):
        disable_rich_logging()

        circuit = make_multiplication_circuit(
            # a=[True, False, True, True], b=[False, True, False, True]
            a=15,
            b=15,
        )
        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True)
        # manim_circuit.shift(DOWN)
        self.add(manim_circuit)

        self.play(manim_circuit.animate_evaluation(speed=2))
        self.wait(3)


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
