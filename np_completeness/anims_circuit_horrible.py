# pyright: ignore
from typing import Callable, cast

from manim import *

from np_completeness.utils.coloring_circuits import *
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import *

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general *

FINAL_VIDEO = False




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

