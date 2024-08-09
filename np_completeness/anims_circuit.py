from typing import Callable, cast

from manim import *

from np_completeness.utils.coloring_circuits import (
    get_example_graph,
    make_coloring_circuit,
)
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import (
    make_adder_circuit,
    make_adder_gate,
    make_example_circuit,
    make_multiplication_circuit,
    to_binary,
)

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import (
    BASE00,
    BLUE,
    MAGENTA,
    RED,
    WIRE_WIDTH,
    default,
    disable_rich_logging,
    get_wire_color,
    text_color,
)

FINAL_VIDEO = False


def make_multiplication_by_hand(
    rows: list[str],
) -> tuple[VGroup, list[list[VMobject]], list[Line]]:
    """Make a visualisation of the "school algorithm" for multiplying by hand."""
    assert all(
        len(row) == len(rows[0]) for row in rows
    ), "All rows must have the same length"

    n_rows, n_cols = len(rows), len(rows[0])

    # Manim refuses to render a single space to TeX, so use an empty object
    numbers: list[list[VMobject]] = [
        [Tex(c, color=BASE00) if c != " " else VGroup() for c in row] for row in rows
    ]

    # Fade out the helper zeroes in the intermediate results
    for i in range(3, len(rows) - 1):
        for j in range(n_cols - i + 2, n_cols):
            assert (
                rows[i][j] == "0"
            ), f"Expected a zero, got {repr(rows[i][j])} at {i}, {j}"
            numbers[i][j].fade(0.5)

    X_SHIFT = RIGHT * 0.45
    Y_SHIFT = DOWN * 0.6

    # There is also Group.arrange_in_grid() but it takes into account the sizes of the
    # objects and that leads to wonky spacing because numbers have different widths.
    for i, row in enumerate(numbers):
        for j, number in enumerate(row):
            number.move_to(
                X_SHIFT * j + Y_SHIFT * i,
            )

    group = VGroup()
    for row in numbers:
        group.add(*row)

    lines = [
        Line(
            -X_SHIFT * 0.5 + Y_SHIFT * 1.5,
            +X_SHIFT * (n_cols - 0.5) + Y_SHIFT * 1.5,
            color=BASE00,
        ),
        Line(
            -X_SHIFT * 0.5 + Y_SHIFT * (n_rows - 1.5),
            +X_SHIFT * (n_cols - 0.5) + Y_SHIFT * (n_rows - 1.5),
            color=BASE00,
        ),
    ]

    group.add(*lines)

    return (group, numbers, lines)


def lagged_create(
    objects: list[VMobject], lag_ratio: float = 0.1, anim: type[Animation] | None = None
) -> AnimationGroup:
    if anim is None:
        anim = Create
    return LaggedStart(*[anim(obj) for obj in objects], lag_ratio=lag_ratio)


class MultiplicationByHand(Scene):
    def construct(self):
        disable_rich_logging()
        default()

        mult_tex = Tex(r"{{$3$}}{{$\,\times\,$}}{{$5$}}{{$\,= ???$}}").scale(4)
        self.play(
            AnimationGroup(
                *[Write(cast(VMobject, mult_tex[i])) for i in range(4)],
                lag_ratio=0.5,
            )
        )
        self.wait(1)
        self.play(FadeOut(mult_tex))
        self.wait()

        grid = [
            "  68",
            "× 18",
            " 544",
            " 680",
            "1224",
        ]
        group, _, _ = make_multiplication_by_hand(grid)
        group.scale(2).to_edge(UP, buff=0.75)

        self.play(FadeIn(group))
        self.wait(2)
        self.play(FadeOut(group))

        grid = [
            "   11",
            "× 101",
            "   11",
            "    0",
            " 1100",
            " 1111",
        ]
        group, numbers, lines = make_multiplication_by_hand(grid)
        group.scale(1.75).center().shift(LEFT * 2).to_edge(UP, buff=0.5)

        base10_rows = [
            Tex("{{=}}{{\\,3}}", color=MAGENTA),
            Tex("{{=}}{{\\,5}}", color=MAGENTA),
            VGroup(),
            VGroup(),
            VGroup(),
            Tex("=\\,15", color=MAGENTA),
        ]

        for i, row in enumerate(base10_rows):
            row.scale(2).next_to(
                numbers[i][-1], direction=RIGHT, buff=1, aligned_edge=DOWN
            )

        # this is what it is in base10
        for j in [1, 0]:
            objects_to_animate = [
                cast(VMobject, base10_rows[0][j]),
                cast(VMobject, base10_rows[1][j]),
            ]
            self.play(lagged_create(objects_to_animate, anim=Write))
            self.wait(0.5)

        self.play(lagged_create(numbers[0] + numbers[1], anim=Write))
        self.wait(1)

        # intermediate results
        self.play(
            lagged_create([lines[0], *numbers[2], *numbers[3], *numbers[4]], anim=Write)
        )
        self.wait(1)
        # final result, explanation in base10
        self.play(lagged_create([lines[1], *numbers[5]], anim=Write))
        self.wait(0.5)
        self.play(lagged_create([base10_rows[5]], anim=Write))
        self.wait(2)


class CircuitScene(Scene):
    def construct(self):
        disable_rich_logging()

        a, b = 3, 5

        circuit = make_multiplication_circuit(a=a, b=b)

        # We want to leave a bit of room at the bottom because of subtitles
        # TODO: is this enough?
        circuit.scale(0.8).shift(LEFT * 0.4 + UP * 0.2)

        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True)

        self.play(Create(manim_circuit, lag_ratio=0.002), run_time=3)
        self.wait()

        TEXT_SCALE = 1.4

        # Add explanations to the inputs
        for symbol, value in zip("ab", [a, b]):
            binary_values = to_binary(value)
            explanations = []
            anims = []

            for i, bit in enumerate(binary_values):
                manim_gate = manim_circuit.gates[f"input_{symbol}_{i}"]

                explanation = (
                    Tex(str(int(bit)), color=BLUE)
                    .scale(TEXT_SCALE)
                    .move_to(
                        manim_gate.get_center()
                        + (
                            np.array([-0.3, 0.3, 0])
                            if symbol == "a"
                            else np.array([-0.3, 0.1, 0])
                        )
                    )
                )
                explanations.append(explanation)

                anims.append(manim_gate.animate_to_value(bit))
                anims.append(Write(explanation))

            decimal_explanation = (
                Tex(f"=\\,{value}", color=MAGENTA)
                .scale(TEXT_SCALE)
                .move_to(
                    np.array(
                        [
                            manim_circuit.gates[f"input_a_0"].get_center()[0] + 0.9,
                            explanations[0].get_center()[1],
                            0,
                        ]
                    )
                )
            )
            anims.append(Write(decimal_explanation))

            self.play(LaggedStart(*anims))
            self.wait()

        self.play(manim_circuit.animate_evaluation())
        self.wait()

        # Add explanations to the outputs
        anims = []
        explanations = []
        for i, bit in enumerate(to_binary(a * b, n_digits=8)):
            manim_gate = manim_circuit.gates[f"output_{i}"]

            explanation = (
                Tex(str(int(bit)), color=BLUE)
                .scale(TEXT_SCALE)
                .move_to(manim_gate.get_center() + np.array([-0.3, -0.3, 0]))
            )
            explanations.append(explanation)

            anims.append(manim_gate.animate_to_value(bit))
            anims.append(Write(explanation))

        decimal_explanation = (
            Tex(f"=\\,{a * b}", color=MAGENTA)
            .scale(TEXT_SCALE)
            .move_to(explanations[0].get_center() + RIGHT * 1.5)
        )
        anims.append(Write(decimal_explanation))

        self.play(LaggedStart(*anims))
        self.wait(2)


class ExampleCircuitScene(Scene):
    def construct(self):
        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit, scale=2)
        self.add(manim_circuit)
        self.wait()

        # Create input labels
        input_values = [0, 1, 1]  # Matching the out_value in make_example_circuit
        input_labels = []
        for i, value in enumerate(input_values):
            color = get_wire_color(bool(value))
            label = Tex(str(value), color=color).scale(1.5)

            input_gate = manim_circuit.gates[f"input_{i}"]
            label.next_to(input_gate, UP, buff=0.2)

            input_labels.append(label)

        internal_gates = [
            gate
            for name, gate in manim_circuit.gates.items()
            if not name.startswith(("input_", "output_"))
        ]

        # highlight the wires
        # TODO somehow this does not work
        for sc in [10, 1]:
            self.play(
                *[
                    wire.animate.set_stroke_width(WIRE_WIDTH * sc)
                    for wire in manim_circuit.wires.values()
                ],
                run_time=0.5,
            )
            self.wait(0.5)

        # highlight the gates
        for sc in [1.5, 1 / 1.5]:
            self.play(
                *[cast(Animation, gate.animate.scale(sc)) for gate in internal_gates],
                run_time=0.5,
            )
            self.wait(0.5)

        # Animate the appearance of input labels
        self.play(
            AnimationGroup(
                *[Write(label) for label in input_labels],
                lag_ratio=0.5,
            )
        )
        self.wait()

        # Animate inputs
        self.play(manim_circuit.animate_inputs())
        self.wait()

        # Simulate the circuit
        self.play(manim_circuit.animate_evaluation())
        self.wait(2)


class AdderCircuitScene(Scene):
    def construct(self):
        circuit = make_adder_gate(inputs=[True, False, True])
        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit)
        self.add(manim_circuit)
        self.wait()

        description_tex = Group(
            *[
                Tex(str, color=text_color)
                for str in [
                    r"In:",
                    r"three bits",
                    r"Out:",
                    r"their sum in binary",
                ]
            ]
        ).arrange_in_grid(rows=2, cell_alignment=LEFT)
        description = Group(description_tex).to_corner(UR)

        self.play(FadeIn(description))
        self.wait()

        detailed_circuit = make_adder_circuit(inputs=[False, False, True])
        detailed_circuit.add_missing_inputs_and_outputs()
        detailed_circuit.shift(RIGHT * 0.5 + DOWN * 0.5)
        detailed_manim_circuit = ManimCircuit(detailed_circuit)

        self.play(
            cast(Animation, manim_circuit.animate.scale(30).fade(1)),
            FadeIn(detailed_manim_circuit, scale=0.1),
            run_time=2,
        )
        self.wait()

        self.play(detailed_manim_circuit.animate_evaluation())

        self.wait(1)


class ColoringCircuitScene(Scene):
    def construct(self):
        graph, coloring = get_example_graph(good_coloring=False)

        self.play(Create(graph, lag_ratio=0.1))

        circuit = make_coloring_circuit(graph, coloring)
        circuit.add_missing_inputs_and_outputs(visible=False)
        manim_circuit = ManimCircuit(circuit)

        self.wait(1)

        self.play(
            Create(manim_circuit, lag_ratio=0.002),
            LaggedStart(
                *[
                    cast(Animation, v.animate.fade(0.5).scale(5))
                    for v in graph.vertices.values()
                ]
            ),
            *[FadeOut(e) for e in graph.edges.values()],
            run_time=3,
        )
        self.wait(2)

        # The idea is that you have one variable per vertex and color
        self.play(manim_circuit.animate_inputs())
        self.wait()

        def make_highlight_rectangles(
            condition: Callable[[str], bool],
        ) -> None:
            evaluation = circuit.evaluate()

            selected_gates = [
                name for name in evaluation.gate_evaluations if condition(name)
            ]
            rectangles = VGroup(
                *[
                    SurroundingRectangle(manim_circuit.gates[gate], color=RED)
                    for gate in selected_gates
                ]
            )
            self.play(Create(rectangles, lag_ratio=0.05))
            self.wait()
            self.play(Uncreate(rectangles, lag_ratio=0.05))
            self.wait()

        make_highlight_rectangles(
            lambda name: name.startswith("vertex_") and not "value" in name
        )

        make_highlight_rectangles(lambda name: name.startswith("edge_"))

        self.play(manim_circuit.animate_evaluation())

        self.wait()

        evaluation = circuit.evaluate()
        make_highlight_rectangles(
            lambda name: "nand" in name
            and not name.startswith("output_")  # auto-generated hidden output nodes
            and not evaluation.get_gate_outputs(name)[0]
        )

        self.wait()


if __name__ == "__main__":
    graph, coloring = get_example_graph(good_coloring=False)
    circuit = make_coloring_circuit(graph, coloring)

    with_evaluation = False
    if with_evaluation:
        circuit.add_missing_inputs_and_outputs()
    circuit.display_graph(with_evaluation=with_evaluation)
