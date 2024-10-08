from typing import Callable, cast

from manim import *

from np_completeness.utils.coloring_circuits import (
    GRAPH_COLORS,
    get_example_graph,
    make_coloring_circuit,
)
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import (
    make_adder_circuit,
    make_adder_gate,
    make_example_circuit,
    make_multiplication_circuit,
    make_multiplication_circuit_constraints,
    to_binary,
)

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import *

FINAL_VIDEO = False


def make_multiplication_by_hand(
    rows: list[str], color: bool = False
) -> tuple[VGroup, list[list[VMobject]], list[Line]]:
    """Make a visualisation of the "school algorithm" for multiplying by hand."""
    assert all(
        len(row) == len(rows[0]) for row in rows
    ), "All rows must have the same length"

    n_rows, n_cols = len(rows), len(rows[0])

    def coloring(c: str) -> str:
        if color is False or c not in "01":
            return BASE00
        return get_wire_color(c == "1")

    # Manim refuses to render a single space to TeX, so use an empty object
    numbers: list[list[VMobject]] = [
        [
            Text(c, color=coloring(c))
            if c == "×"
            else (Tex(c, color=coloring(c)) if c != " " else VGroup())
            for c in row
        ]
        for row in rows
    ]

    # Fade out the helper zeroes in the intermediate results
    for i in range(3, len(rows) - 1):
        for j in range(n_cols - i + 2, n_cols):
            assert (
                rows[i][j] == "0"
            ), f"Expected a zero, got {repr(rows[i][j])} at {i}, {j}"
            numbers[i][j].fade(0.6)

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

        mult_tex = Tex(r"{{$3$}}{{$\,\times\,$}}{{$5$}}{{$\,=\,???$}}").scale(4)
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
        group, numbers, lines = make_multiplication_by_hand(grid, color=True)
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


def make_multiplication_explanation_texts(
    manim_circuit: ManimCircuit, a: int, b: int, text_scale: float
) -> tuple[list[list[VMobject]], list[list[Animation]]]:
    """Create texts next to the multiplication inputs explaining the binary."""
    # Add explanations to the inputs
    all_explanations, all_anims = [], []

    for symbol, value in zip("ab", [a, b]):
        binary_values = to_binary(value)
        explanations = []
        anims = []

        for i, bit in enumerate(binary_values):
            manim_gate = manim_circuit.gates[f"input_{symbol}_{i}"]

            explanation = (
                Tex(str(int(bit)), color=BLUE)
                .scale(text_scale)
                .move_to(
                    manim_gate.get_center()
                    + (
                        np.array([0.1, 0.35, 0])
                        if symbol == "a"
                        else np.array([0.1, 0.35, 0])
                    )
                )
            )
            explanations.append(explanation)

            anims.append(manim_gate.animate_to_value(bit))
            anims.append(Write(explanation))

        decimal_explanation = (
            Tex(f"=\\,{value}", color=MAGENTA)
            .scale(text_scale)
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
        explanations.append(decimal_explanation)
        anims.append(Write(decimal_explanation))

        all_explanations.append(explanations)
        all_anims.append(anims)

    return all_explanations, all_anims


class MultiplicationCircuitScene(Scene):
    def construct(self):
        disable_rich_logging()

        a, b = 3, 5

        circuit = make_multiplication_circuit(a=a, b=b)

        # We want to leave a bit of room at the bottom because of subtitles
        # TODO: is this enough?
        # NOTE: Keep in sync with GreaterThanOneConstraint
        circuit.scale(0.8).shift(LEFT * 0.4 + UP * 0.2)

        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True)

        self.play(Create(manim_circuit, lag_ratio=0.002), run_time=3)
        self.wait()

        rect = SurroundingRectangle(
            Group(
                *[manim_circuit.gates[f"input_a_{i}"] for i in range(4)],
                *[manim_circuit.gates[f"input_b_{i}"] for i in range(4)],
            ),
            color=RED,
        )
        self.play(Create(rect))
        self.play(FadeOut(rect))
        self.wait()

        TEXT_SCALE = 1.4
        _all_explanations, all_anims = make_multiplication_explanation_texts(
            manim_circuit, a, b, text_scale=TEXT_SCALE
        )

        for i in range(2):
            self.play(LaggedStart(*all_anims[i]))

        self.play(manim_circuit.animate_evaluation(scene=self))
        self.wait()

        # Add explanations to the outputs
        anims = []
        explanations = []
        for i, bit in enumerate(to_binary(a * b, n_digits=8)):
            manim_gate = manim_circuit.gates[f"output_{i}"]

            explanation = (
                Tex(str(int(bit)), color=BLUE)
                .scale(TEXT_SCALE)
                .move_to(manim_gate.get_center() + np.array([00, -0.45, 0]))
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


class GreaterThanOneConstraint(Scene):
    def construct(self):
        a, b = 1, 15
        circuit = make_multiplication_circuit_constraints(a, b)
        # NOTE: Keep in sync with MultiplicationCircuitScene
        circuit.scale(0.8).shift(LEFT * 0.4 + UP * 0.2)

        manim_circuit = ManimCircuit(circuit)

        for manim_gate in manim_circuit.gates.values():
            if manim_gate.gate.visual_type in ["not", "or", "and"]:
                manim_gate.scale(2)

        self.add(manim_circuit)
        self.wait()

        TEXT_SCALE = 1.4
        all_explanations, all_anims = make_multiplication_explanation_texts(
            manim_circuit, a, b, text_scale=TEXT_SCALE
        )

        for i in range(2):
            self.play(LaggedStart(*all_anims[i]))

        self.wait()
        self.play(manim_circuit.animate_evaluation(scene=self))
        self.wait()
        self.play(
            Create(SurroundingRectangle(all_explanations[0][-1], color=RED)),
            Create(SurroundingRectangle(manim_circuit.gates["or_a"], color=RED)),
        )
        self.wait()


class ExampleCircuitScene(Scene):
    def construct(self):
        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit, scale=2)
        self.add(manim_circuit)
        self.wait()

        # Create input labels
        input_values = [1, 1, 0]  # Matching the out_value in make_example_circuit
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
                *[
                    cast(Animation, gate.animate.scale(sc))
                    for gate in internal_gates
                    if gate.gate.visual_type != "knot"
                ],
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
        self.play(manim_circuit.animate_evaluation(scene=self))

        # add output labels
        output_labels = [
            Tex(str(val), color=get_wire_color(True if val == 1 else False))
            .scale(1.5)
            .next_to(manim_circuit.gates["output_" + str(i)], dir)
            for val, i, dir in [(1, 0, LEFT), (0, 1, RIGHT)]
        ]
        self.play(
            AnimationGroup(
                *[Write(label) for label in output_labels],
                lag_ratio=0.5,
            )
        )
        self.wait()


class AdderCircuitScene(Scene):
    def construct(self):
        circuit = make_adder_gate(inputs=[True, False, True])
        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, scale=2, wire_scale=1)
        self.add(manim_circuit)
        self.wait()

        description_tex = Tex(
            r"\hbox{\hbox to 9mm{In:\hss}three bits}\hbox{\hbox to 9mm{Out:\hss}their sum in binary}",
            color=text_color,
        )
        description = Group(description_tex).to_corner(UR)

        self.play(FadeIn(description))
        self.wait()

        detailed_circuit = make_adder_circuit(inputs=[True, False, True])
        detailed_circuit.add_missing_inputs_and_outputs()
        detailed_manim_circuit = ManimCircuit(detailed_circuit)
        detailed_manim_circuit.shift(RIGHT * 0.5 + DOWN * 0.5)

        self.play(
            animate(manim_circuit).scale(15).set_stroke_width(15).fade(1),
            FadeIn(detailed_manim_circuit, scale=0.1),
            run_time=2,
        )
        self.wait()

        self.play(detailed_manim_circuit.animate_evaluation(scene=self))

        self.wait(1)


class ColoringCircuitScene(Scene):
    def construct(self):
        graph, coloring = get_example_graph(good_coloring=True, colored=False)
        graph.shift(0.2 * UP)

        self.play(Create(graph, lag_ratio=0.1))
        self.wait()

        self.play(
            AnimationGroup(
                *[
                    graph.vertices[vertex].animate.set_fill_color(
                        GRAPH_COLORS[coloring[vertex]]
                    )
                    for vertex in graph.vertices
                ],
                lag_ratio=0.75,
            )
        )
        self.wait()

        rectangle = SurroundingRectangle(graph.vertices[4], color=RED)
        self.play(Create(rectangle))
        self.play(animate(graph.vertices[4]).set_color(GRAPH_COLORS[0]))
        coloring[4] = 0
        self.play(Uncreate(rectangle))
        self.wait()
        self.play(
            Indicate(graph.vertices[4], scale_factor=1.5, color=GRAPH_COLORS[0]),
            Indicate(graph.vertices[5], scale_factor=1.5, color=GRAPH_COLORS[0]),
        )
        self.wait()

        circuit, circuit2 = [
            make_coloring_circuit(
                graph, coloring, output_position=np.array([-4, -2.0, 0])
            )
            for _ in range(2)
        ]
        manim_circuit, manim_circuit2 = ManimCircuit(circuit), ManimCircuit(circuit2)

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
        self.wait()

        # Fade out the wires that lead to the output gate
        anims = []
        for (_wire_start, wire_end), manim_wire in manim_circuit.wires.items():
            if wire_end == "big_and":
                anims.append(animate(manim_wire).fade(0.9))
        self.play(*anims)
        self.wait()

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
            lambda name: name.startswith("vertex_")
            and not "value" in name
            or name.startswith("edge_")
        )

        make_highlight_rectangles(lambda name: name == "output")

        self.play(manim_circuit.animate_evaluation(scene=self))
        self.wait()

        evaluation = circuit.evaluate()
        make_highlight_rectangles(
            lambda name: "nand" in name
            and not name.startswith("output_")  # auto-generated hidden output nodes
            and not evaluation.get_gate_outputs(name)[0]
        )

        self.wait()
        self.play(
            FadeOut(manim_circuit),
            FadeIn(manim_circuit2),
        )
        self.wait()

        out_tex = (
            Tex(r"$x_{\text{output}} = 1$", color=WIRE_COLOR_TRUE)
            .scale(0.8)
            .next_to(manim_circuit.gates["output"], LEFT)
        )
        self.play(Write(out_tex))
        self.wait()


if __name__ == "__main__":
    graph, coloring = get_example_graph(good_coloring=False)
    circuit = make_coloring_circuit(graph, coloring)

    with_evaluation = False
    if with_evaluation:
        circuit.add_missing_inputs_and_outputs()
    circuit.display_graph(with_evaluation=with_evaluation)
