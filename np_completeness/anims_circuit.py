# pyright: ignore
from typing import Callable, cast

from manim import *

from np_completeness.utils.coloring_circuits import (
    get_example_graph,
    make_coloring_circuit,
)
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import (
    make_adder_circuit,
    make_example_circuit,
    make_multiplication_circuit,
    to_binary,
)

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import (
    BACKGROUND_COLOR,
    BASE00,
    BLUE,
    CNF_CONSTRAINTS,
    MAGENTA,
    RED,
    WIRE_COLOR_FALSE,
    WIRE_COLOR_TRUE,
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


class ShowConstraints(Scene):
    def construct(self):
        default()

        self.next_section(skip_animations=True)
        circuit = make_multiplication_circuit(a=7, b=4)
        circuit.scale(0.8).shift(LEFT * 0.4 + UP * 0.2)
        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True)
        self.play(Create(manim_circuit, lag_ratio=0.002), run_time=3)
        self.wait()

        def clause_to_text(clause):
            terms = []
            for literal in clause:
                if literal < 0:
                    terms.append(r"(NOT$\,x_{" + str(abs(literal)) + r"}$)")
                else:
                    terms.append(r"$\,x_{" + str(abs(literal)) + r"}$")
            return r"$\, \text{OR} \,$".join(terms)

        # Create Tex objects for each clause
        clause_texts = [
            Tex(clause_to_text(clause), font_size=20, color=text_color)
            for clause in (CNF_CONSTRAINTS if FINAL_VIDEO else CNF_CONSTRAINTS[:10])
        ]
        clause_texts = [
            Group(
                SurroundingRectangle(
                    clause,
                    stroke_width=0,
                    buff=0,
                    fill_opacity=1.0,
                    fill_color=BACKGROUND_COLOR,
                ),
                clause,
            )
            for clause in clause_texts
        ]
        # Arrange clauses in a table
        table = Group(*clause_texts).arrange_in_grid(
            cols=3, aligned_edge=LEFT, cell_alignment=LEFT, buff=0.25
        )

        surrounding_rectangle = SurroundingRectangle(
            table,
            buff=0.5,
            color=text_color,
            fill_opacity=1.0,
            fill_color=BACKGROUND_COLOR,
        )

        # Group everything together
        full_display = Group(surrounding_rectangle, table)

        # Center the display on the screen
        full_display.to_edge(UP)

        # Animation
        self.play(FadeIn(full_display))
        self.wait()
        self.play(
            full_display.animate.to_edge(DOWN),
        )
        self.wait()

        self.play(FadeOut(surrounding_rectangle))

        radius = 1.5
        angles = np.linspace(0, 2 * np.pi, len(clause_texts), endpoint=False)

        positions = []
        for _, angle in zip(clause_texts, angles):
            new_pos = (
                np.random.rand() * radius * np.array([np.cos(angle), np.sin(angle), 0])
            )
            positions.append(new_pos)

        self.play(
            AnimationGroup(
                *[
                    clause.animate.move_to(new_pos)
                    for clause, new_pos in zip(clause_texts, positions)
                ]
            )
        )
        self.wait()

        circuit_logic_text = Tex(
            r"Circuit \\ Logic", color=text_color, z_index=10
        ).scale(1.5)
        new_rectangle = SurroundingRectangle(
            circuit_logic_text,
            color=text_color,
            fill_opacity=1.0,
            fill_color=BACKGROUND_COLOR,
        )
        new_rectangle.set_width(4.5)

        self.play(
            Create(new_rectangle),
            Write(circuit_logic_text),
            *[FadeOut(clause) for clause in clause_texts],
        )
        self.wait()
        logic_group = Group(circuit_logic_text, new_rectangle)
        self.play(logic_group.animate.to_corner(UR, buff=0.0).shift(0.3 * DL))

        self.wait(2)

        arrow = Arrow(
            start=logic_group.get_bottom() + 1 * LEFT,
            end=logic_group.get_bottom() + 1 * LEFT + 1.5 * DOWN,
            buff=0.1,
        )
        sat_solver_text = Tex("SAT-solver").next_to(arrow, RIGHT)
        running_text = (
            Tex(r"\raggedright running the circuit \\ on some input")
            .next_to(arrow.get_end(), DOWN)
            .to_edge(RIGHT, buff=0.5)
        )
        sat_group = VGroup(arrow, sat_solver_text)

        self.next_section(skip_animations=False)
        self.play(Create(arrow), Write(sat_solver_text))
        self.wait()
        self.play(Write(running_text))
        self.play(manim_circuit.animate_evaluation(speed=2))
        self.wait()

        self.wait()
        self.play(FadeOut(sat_group), FadeOut(running_text))
        self.wait()

        a, b = 5, 3
        number_a = (
            Tex(f"{a}", color=text_color)
            .scale(1.4)
            .next_to(logic_group, DOWN, buff=0.5)
            .align_to(logic_group, LEFT)
        )
        number_b = (
            Tex(f"{b}", color=text_color).scale(1.4).next_to(number_a, DOWN, buff=1.5)
        )

        self.play(Write(number_a), Write(number_b))
        self.wait()

        binary_a = (
            Tex(
                r"{{$ = \,$}}{{$0\, $}}{{$1\, $}}{{$0\, $}}{{$1\, $}}}",
                color=text_color,
            )
            .scale(1.2)
            .next_to(number_a, RIGHT, buff=0.1)
        )
        binary_b = (
            Tex(
                r"{{$ = \,$}}{{$0\, $}}{{$0\, $}}{{$1\, $}}{{$1\, $}}}",
                color=text_color,
            )
            .scale(1.2)
            .next_to(number_b, RIGHT, buff=0.1)
        )

        for i in range(4):
            binary_a[4 - i].set_color(
                (WIRE_COLOR_FALSE if (a & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )
            binary_b[4 - i].set_color(
                (WIRE_COLOR_FALSE if (a & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )

        self.play(Write(binary_a), Write(binary_b))
        self.wait()

        # change bits to constraints
        constraint_a, constraint_b = [], []
        eqs_a, eqs_b = [], []
        for c, constraint, eqs in zip(
            [a, b], [constraint_a, constraint_b], [eqs_a, eqs_b]
        ):
            for i in range(4):
                col = WIRE_COLOR_FALSE if (c & (1 << i)) == 0 else WIRE_COLOR_TRUE
                st = r"$x_{" + str((i if c == a else i + 4)) + r"}$"
                eqst = r"$x_{" + str((i if c == a else i + 4)) + r"} = $"
                if (c & (1 << i)) == 0:
                    st = r"NOT " + st
                    eqst = eqst + "0"
                else:
                    eqst = eqst + "1"
                constraint.append(Tex(st, color=col))
                eqs.append(Tex(eqst, color=col))

        constraint_a = Group(*constraint_a).arrange_in_grid(rows=2, cell_alignment=LEFT)
        eqs_a = Group(*eqs_a).arrange_in_grid(rows=2, cell_alignment=LEFT)
        constraint_b = Group(*constraint_b).arrange_in_grid(rows=2, cell_alignment=LEFT)
        eqs_b = Group(*eqs_b).arrange_in_grid(rows=2, cell_alignment=LEFT)

        constraints = (
            Group(*constraint_a, *constraint_b)
            .arrange_in_grid(rows=4, cell_alignment=LEFT)
            .next_to(logic_group, DOWN, buff=0.5)
        )
        eqs = (
            Group(*eqs_a, *eqs_b)
            .arrange_in_grid(rows=4, cell_alignment=LEFT)
            .next_to(logic_group, DOWN, buff=0.5)
        )
        Group(constraint_b, eqs_b).shift(0.5 * DOWN)

        # Change binary numbers to constraints
        self.play(
            *[ReplacementTransform(binary_a[i + 1], constraint_a[i]) for i in range(4)],
            *[ReplacementTransform(binary_b[i + 1], constraint_b[i]) for i in range(4)],
            FadeOut(number_a),
            FadeOut(number_b),
            FadeOut(binary_a[0]),
            FadeOut(binary_b[0]),
        )
        self.wait()

        self.play(
            *[ReplacementTransform(constraint_a[i], eqs_a[i]) for i in range(4)],
            *[ReplacementTransform(constraint_b[i], eqs_b[i]) for i in range(4)],
        )
        self.wait()

        # Scale down the equation text
        new_eqs_a, new_eqs_b = [], []
        for eqs in [eqs_a, eqs_b]:
            for eq in eqs:
                eq.generate_target()
                eq.target.scale(0.5)
                if eqs == eqs_a:
                    new_eqs_a.append(eq.target)
                else:
                    new_eqs_b.append(eq.target)
        new_eqs_a = Group(*new_eqs_a).arrange_in_grid(rows=1)
        new_eqs_b = (
            Group(*new_eqs_b).arrange_in_grid(rows=1).next_to(new_eqs_a, DOWN, buff=0.3)
        )
        rec = Rectangle(
            width=logic_group[1].get_width(),
            height=Group(new_eqs_a, new_eqs_b).get_height() + 0.5,
            color=text_color,
        ).move_to(Group(new_eqs_a, new_eqs_b).get_center())
        input_group = Group(rec, new_eqs_a, new_eqs_b).next_to(
            logic_group, DOWN, buff=0.5
        )

        self.play(
            *[MoveToTarget(eq) for eq in eqs_a],
            *[MoveToTarget(eq) for eq in eqs_b],
            Create(input_group[0]),
        )
        self.wait()
        sat_group.next_to(input_group, DOWN, buff=0.5)
        self.play(FadeIn(sat_group))
        self.wait()
        mult_tex = Tex(r"Multiplying $3 \times 5$", color=text_color).next_to(
            sat_group, DOWN, buff=0.5
        )
        self.play(
            Write(mult_tex),
        )
        self.wait()

        return

        # Move bits to the respective input wires
        for i, bit in enumerate(to_binary(a, n_digits=4)):
            manim_gate = manim_circuit.gates[f"input_a_{i}"]
            bit_text = (
                Tex(str(int(bit)), color=BLUE)
                .scale(1.2)
                .move_to(binary_a.get_center() + RIGHT * (i - 1.5))
            )

            self.play(
                Transform(bit_text, bit_text.copy().move_to(manim_gate.get_center()))
            )
            self.wait(0.5)

        for i, bit in enumerate(to_binary(b, n_digits=4)):
            manim_gate = manim_circuit.gates[f"input_b_{i}"]
            bit_text = (
                Tex(str(int(bit)), color=BLUE)
                .scale(1.2)
                .move_to(binary_b.get_center() + RIGHT * (i - 1.5))
            )

            self.play(
                Transform(bit_text, bit_text.copy().move_to(manim_gate.get_center()))
            )
            self.wait(0.5)

        self.wait()
        self.play(manim_circuit.animate_evaluation(speed=2))
        self.wait()


if __name__ == "__main__":
    graph, coloring = get_example_graph(good_coloring=False)
    circuit = make_coloring_circuit(graph, coloring)

    with_evaluation = False
    if with_evaluation:
        circuit.add_missing_inputs_and_outputs()
    circuit.display_graph(with_evaluation=with_evaluation)
