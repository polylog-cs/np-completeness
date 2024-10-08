import random

from manim import *

from np_completeness.utils.cnf_constraints import CNF_CONSTRAINTS
from np_completeness.utils.coloring_circuits import *
from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import *
from np_completeness.utils.util_general import *

"""

from utils.cnf_constraints import CNF_CONSTRAINTS
from utils.coloring_circuits import *
from utils.manim_circuit import ManimCircuit
from utils.specific_circuits import *
from utils.util_general import *
"""


FINAL_VIDEO = True
CIRCUIT_LABEL_SCALE = 0.8
TBL_SCALE = 0.6


class ShowConstraints(Scene):
    def construct(self):
        default()

        self.next_section(skip_animations=False)

        circuits = []
        manim_circuits = []
        for i, (a, b, rev) in enumerate(
            [
                (7, 4, False),
                (5, 3, False),
                (1, 15, True),
                (3, 5, True),
                (13, 1, True),
                (2, 7, False),
            ]
        ):
            circuit = make_multiplication_circuit(a=a, b=b)
            circuit.scale(0.8).shift(LEFT * 0.4 + UP * 0.2)
            circuit.add_missing_inputs_and_outputs()
            if rev:
                circuit = circuit.reverse()
            manim_circuit = (
                ManimCircuit(circuit, with_evaluation=True, wire_scale=0.75)
                .scale(0.75)
                .to_edge(LEFT)
            )

            circuits.append(circuit)
            manim_circuits.append(manim_circuit)

        circuit, manim_circuit = circuits[0], manim_circuits[0]
        self.play(Create(manim_circuit, lag_ratio=0.002), run_time=3)
        self.wait()

        def clause_to_text(clause: list[int]) -> str:
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
            for clause in CNF_CONSTRAINTS[: -1 if FINAL_VIDEO else 3]
        ]
        # Arrange clauses in a table
        table = Group(*clause_texts).arrange_in_grid(
            cols=3, aligned_edge=LEFT, cell_alignment=LEFT, buff=0.25
        )

        surrounding_rectangle = SurroundingRectangle(
            table,
            buff=0.5,
            color=text_color,
            stroke_width=0,
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
            animate(full_display).to_edge(DOWN),
        )
        self.wait()

        radius = 1
        angles = np.linspace(0, 2 * np.pi, len(clause_texts), endpoint=False)
        rrr = 4.5 * RIGHT
        positions = []
        np.random.seed(0)
        for _, angle in zip(clause_texts, angles):
            new_pos = (
                np.random.rand() * radius * np.array([np.cos(angle), np.sin(angle), 0])
            )
            new_pos[1] *= 0.5
            positions.append(new_pos)

        random.seed(0)
        vis = list(range(len(clause_texts)))
        random.shuffle(vis)
        vis = set(vis[:30])

        self.play(
            FadeOut(surrounding_rectangle),
            AnimationGroup(
                *[
                    animate(clause).move_to(new_pos).shift(rrr).fade(int(i not in vis))
                    for i, (clause, new_pos) in enumerate(zip(clause_texts, positions))
                ]
            ),
        )
        self.wait()
        new_clauses = []
        for i, clause_text in enumerate(clause_texts):
            if i not in vis:
                self.remove(clause_texts[i])
            else:
                new_clauses.append(clause_text)
        clause_texts = new_clauses
        for clause in clause_texts:
            clause.set_z_index(-10)

        circuit_logic_text = (
            Tex(r"Circuit Logic", color=text_color, z_index=-5).scale(1.25).shift(rrr)
        ).set_z_index(-5)
        new_rectangle = SurroundingRectangle(
            VGroup(circuit_logic_text, *clause_texts),
            buff=0,
            fill_opacity=0.7,
            fill_color=BACKGROUND_COLOR,
            stroke_width=0,
        ).set_z_index(-8)

        self.play(
            FadeIn(new_rectangle),
            Write(circuit_logic_text),
            # *[FadeOut(clause) for clause in clause_texts],
        )
        self.wait()
        logic_group = Group(*clause_texts, circuit_logic_text, new_rectangle)
        self.play(animate(logic_group).move_to(3 * UP + 4.3 * RIGHT))

        self.wait(2)

        arrow = Arrow(
            start=logic_group.get_bottom() + 1 * LEFT,
            end=logic_group.get_bottom() + 1 * LEFT + 1.5 * DOWN,
            buff=0.1,
        ).shift(0.8 * DOWN)
        sat_solver_text = Tex("SAT solver").next_to(arrow, RIGHT)
        running_text = (
            Tex(r"\raggedright running the circuit \\ on some input")
            .next_to(arrow.get_end(), DOWN, buff=1)
            .to_edge(RIGHT, buff=0.5)
        )
        sat_group = VGroup(arrow, sat_solver_text)

        self.next_section(skip_animations=False)

        self.play(GrowArrow(arrow), Write(sat_solver_text))
        self.wait()
        self.play(Write(running_text))
        self.play(manim_circuit.animate_evaluation(scene=self, speed=2))
        self.wait()

        self.play(
            FadeOut(manim_circuit),
            FadeIn(manim_circuits[-1]),
        )
        self.play(manim_circuits[-1].animate_evaluation(scene=self, speed=2))
        self.wait()

        self.play(
            FadeOut(sat_group),
            FadeOut(running_text),
            FadeOut(manim_circuits[-1]),
            FadeIn(manim_circuits[1]),
        )
        self.wait()

        a, b = 5, 3
        number_a = (
            Tex(f"{a}", color=text_color)
            .scale(1.4)
            .next_to(logic_group, DOWN, buff=0.5)
            .align_to(logic_group, LEFT)
        ).shift(1 * RIGHT)
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
            .next_to(number_a, RIGHT, buff=0.15)
        )
        binary_b = (
            Tex(
                r"{{$ = \,$}}{{$0\, $}}{{$0\, $}}{{$1\, $}}{{$1\, $}}}",
                color=text_color,
            )
            .scale(1.2)
            .next_to(number_b, RIGHT, buff=0.15)
        )

        for i in range(4):
            binary_a[4 - i].set_color(
                (WIRE_COLOR_FALSE if (a & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )
            binary_b[4 - i].set_color(
                (WIRE_COLOR_FALSE if (b & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )

        self.next_section(skip_animations=False)
        self.play(Write(binary_a), Write(binary_b))
        self.wait()

        # change bits to constraints
        constraint_a, constraint_b = [], []
        eqs_a, eqs_b = [], []
        for c, constraint, eqs in zip(
            [a, b], [constraint_a, constraint_b], [eqs_a, eqs_b]
        ):
            for i in range(4):
                bit = (c & (1 << (3 - i))) != 0
                col = WIRE_COLOR_FALSE if not bit else WIRE_COLOR_TRUE
                st = r"$x_{" + str((i + 1 if c == a else i + 5)) + r"}$"
                eqst = r"{{$x_{" + str((i + 1 if c == a else i + 5)) + r"}=\,$}}"
                if not bit:
                    st = r"NOT " + st
                    eqst = eqst + r"{{$0$}}"
                else:
                    eqst = eqst + r"{{$1$}}"
                constraint.append(Tex(st, color=col))
                eqs.append(Tex(eqst, color=col))

        constraint_a = Group(*constraint_a)
        constraint_b = Group(*constraint_b)
        eqs_a = Group(*eqs_a)
        eqs_b = Group(*eqs_b)
        Group(*constraint_a, *constraint_b).arrange_in_grid(
            rows=4, cell_alignment=DL
        ).next_to(logic_group, DOWN, buff=0.5)
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

        # Scale down the equation text
        new_eqs_a, new_eqs_b = [], []
        for eqs in [eqs_a, eqs_b]:
            for eq in eqs:
                # target = eq.generate_target()
                eq.scale(TBL_SCALE)
                if eqs == eqs_a:
                    new_eqs_a.append(eq)
                else:
                    new_eqs_b.append(eq)
        new_eqs_a = Group(*new_eqs_a).arrange_in_grid(rows=1)
        new_eqs_b = (
            Group(*new_eqs_b).arrange_in_grid(rows=1).next_to(new_eqs_a, DOWN, buff=0.3)
        )
        rec = Rectangle(
            width=logic_group[1].get_width(),
            height=Group(new_eqs_a, new_eqs_b).get_height() + 0.5,
            color=text_color,
            stroke_width=0,
        ).move_to(Group(new_eqs_a, new_eqs_b).get_center())
        input_group = Group(rec, new_eqs_a, new_eqs_b).next_to(
            logic_group, DOWN, buff=0.2
        )

        self.play(
            *[ReplacementTransform(constraint_a[i], eqs_a[i]) for i in range(4)],
            *[ReplacementTransform(constraint_b[i], eqs_b[i]) for i in range(4)],
        )
        self.wait()

        ############################################################################################################
        self.play(
            # *[MoveToTarget(eq) for eq in eqs_a],
            # *[MoveToTarget(eq) for eq in eqs_b],
            Create(rec),
        )
        self.wait()
        sat_group.next_to(input_group, DOWN, buff=0.5)
        self.play(FadeIn(sat_group))
        self.wait()
        mult_tex = Tex(r"Multiplying $3 \times 5$", color=text_color).next_to(
            sat_group, DOWN, buff=0.5
        )

        inp_a = [tx[1].copy() for tx in eqs_a]
        inp_b = [tx[1].copy() for tx in eqs_b]
        self.play(
            *[
                animate(inp)
                .move_to(manim_circuit.gates[f"input_a_{i}"])
                .scale(1.5)
                .shift(0.3 * UP + 0.05 * RIGHT)
                for i, inp in enumerate(reversed(inp_a))
            ],
            *[
                animate(inp)
                .move_to(manim_circuit.gates[f"input_b_{i}"])
                .scale(1.5)
                .shift(0.3 * UP + 0.05 * RIGHT)
                for i, inp in enumerate(reversed(inp_b))
            ],
        )
        self.wait()

        self.play(
            manim_circuits[1].animate_evaluation(scene=self, speed=2),
            Write(mult_tex),
        )
        self.wait()

        self.play(
            FadeOut(sat_group),
            FadeOut(input_group),
            FadeOut(mult_tex),
            FadeOut(eqs_a),
            FadeOut(eqs_b),
            FadeOut(manim_circuits[1]),
            FadeIn(manim_circuits[2]),
            FadeOut(Group(*inp_a)),
            FadeOut(Group(*inp_b)),
        )
        self.wait()

        #
        #
        #
        #
        #
        #
        #
        self.next_section(skip_animations=False)

        c = 15
        number_c = (
            Tex(f"{c}", color=text_color)
            .scale(1.4)
            .next_to(logic_group, DOWN, buff=0.5)
            .align_to(logic_group, LEFT)
        )

        self.play(Write(number_c))
        self.wait()

        binary_c = (
            Tex(
                r"{{$ = \,$}}{{$0\, $}}{{$0\, $}}{{$0\, $}}{{$0\, $}}{{$1\, $}}{{$1\, $}}{{$1\, $}}{{$1\, $}}",
                color=text_color,
            )
            .scale(1.2)
            .next_to(number_c, RIGHT, buff=0.15)
        )

        for i in range(8):
            binary_c[8 - i].set_color(
                (WIRE_COLOR_FALSE if (c & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )

        self.play(Write(binary_c))
        self.wait()

        # change bits to constraints
        constraint_c = []
        eqs_c = []
        for i in range(8):
            bit = (c & (1 << (7 - i))) != 0
            col = WIRE_COLOR_FALSE if not bit else WIRE_COLOR_TRUE
            st = r"$x_{" + str(i + 74) + r"}$"
            eqst = r"{{$x_{" + str(i + 74) + r"} = $}}"
            if not bit:
                st = r"NOT " + st
                eqst = eqst + r"{{$\,0$}}"
            else:
                eqst = eqst + r"{{$\,1$}}"
            constraint_c.append(Tex(st, color=col))
            eqs_c.append(Tex(eqst, color=col))

        constraint_c = (
            Group(*constraint_c)
            .arrange_in_grid(rows=4, cell_alignment=LEFT)
            .next_to(logic_group, DOWN, buff=0.5)
        )
        eqs_c = (
            Group(*eqs_c)
            .arrange_in_grid(rows=4, cell_alignment=LEFT)
            .next_to(logic_group, DOWN, buff=0.5)
        )

        # Scale down the equation text
        new_eqs_c = []
        for eq in eqs_c:
            # target = eq.generate_target()
            eq.scale(TBL_SCALE)
            new_eqs_c.append(eq)

        new_eqs_c = Group(*new_eqs_c).arrange_in_grid(rows=2)
        rec = Rectangle(
            width=logic_group[1].get_width(),
            height=Group(new_eqs_c).get_height() + 0.5,
            color=text_color,
            stroke_width=0,
        ).move_to(new_eqs_c)
        input_group = Group(rec, new_eqs_c).next_to(logic_group, DOWN, buff=0.2)

        # Change binary numbers to constraints
        self.play(
            *[ReplacementTransform(binary_c[i + 1], eqs_c[i]) for i in range(8)],
            FadeOut(number_c),
            FadeOut(binary_c[0]),
            Create(rec),
        )
        self.wait()

        sat_group.next_to(input_group, DOWN, buff=0.5)
        self.play(FadeIn(sat_group))
        self.wait()
        mult_tex = Tex(r"Factoring 15", color=text_color).next_to(
            sat_group, DOWN, buff=0.5
        )

        inp_c = [tx[1].copy() for tx in eqs_c]
        self.play(
            *[
                animate(inp)
                .scale(CIRCUIT_LABEL_SCALE / TBL_SCALE)
                .move_to(manim_circuit.gates[f"output_{i}"])
                .shift(0.3 * DOWN)
                for i, inp in enumerate(reversed(inp_c))
            ],
        )
        self.wait()

        # show questionmarks next to inputs
        questionmarks = Group(
            *[
                Tex("?", color=text_color)
                .scale(CIRCUIT_LABEL_SCALE)
                .move_to(manim_circuit.gates[f"input_a_{i}"])
                .shift(0.3 * UP + 0.05 * RIGHT)
                for i in range(4)
            ],
            *[
                Tex("?", color=text_color)
                .scale(CIRCUIT_LABEL_SCALE)
                .move_to(manim_circuit.gates[f"input_b_{i}"])
                .shift(0.3 * UP + 0.05 * RIGHT)
                for i in range(4)
            ],
        )

        self.play(
            AnimationGroup(
                *[FadeIn(qm) for qm in questionmarks],
                lag_ratio=0.5,
            )
        )
        self.wait()

        self.play(
            manim_circuits[2].animate_evaluation(scene=self, speed=2),
            Write(mult_tex),
        )
        self.wait()

        a, b, fadeout_qms = 1, 15, True

        binary_a = format(a, "04b")  # 4-bit binary representation of a
        binary_b = format(b, "04b")  # 4-bit binary representation of b

        # Create Tex objects for the binary digits of a and b with correct indices
        bit_texts_a = [
            Tex(
                f"{bit}", color=(WIRE_COLOR_FALSE if int(bit) == 0 else WIRE_COLOR_TRUE)
            ).scale(CIRCUIT_LABEL_SCALE)
            for bit in reversed(binary_a)
        ]
        bit_texts_b = [
            Tex(
                f"{bit}", color=(WIRE_COLOR_FALSE if int(bit) == 0 else WIRE_COLOR_TRUE)
            ).scale(CIRCUIT_LABEL_SCALE)
            for bit in reversed(binary_b)
        ]

        # Arrange the bits next to the input gates
        for i, bit_text in enumerate(bit_texts_a):
            bit_text.move_to(manim_circuit.gates[f"input_a_{i}"]).shift(
                0.3 * UP + 0.05 * RIGHT
            )

        for i, bit_text in enumerate(bit_texts_b):
            bit_text.move_to(manim_circuit.gates[f"input_b_{i}"]).shift(
                0.3 * UP + 0.05 * RIGHT
            )

        # Group the bits for a and b
        bits_group_a = VGroup(*bit_texts_a)
        bits_group_b = VGroup(*bit_texts_b)

        # Animate the appearance of the bits
        anims = [FadeIn(bits_group_a), FadeIn(bits_group_b)]
        if fadeout_qms:
            anims += [FadeOut(questionmarks)]
        self.play(*anims)
        self.wait()

        a_tex = (
            Tex(f"=\\,{a}", color=MAGENTA)
            .scale(CIRCUIT_LABEL_SCALE)
            .next_to(bits_group_a, RIGHT, buff=1)
        )
        b_tex = (
            Tex(f"=\\,{b}", color=MAGENTA)
            .scale(CIRCUIT_LABEL_SCALE)
            .next_to(bits_group_b, RIGHT, buff=1)
            .align_to(a_tex, LEFT)
        )

        self.play(Write(a_tex), Write(b_tex))
        self.wait()

        self.next_section(skip_animations=False)
        self.play(
            FadeOut(manim_circuits[2]),
            FadeIn(manim_circuits[3]),
            FadeOut(a_tex),
            FadeOut(b_tex),
            FadeOut(bits_group_a),
            FadeOut(bits_group_b),
        )
        self.wait()
        self.play(
            manim_circuits[3].animate_evaluation(scene=self, speed=2),
            Write(mult_tex),
        )
        self.wait()

        a, b, fadeout_qms = 3, 5, False

        binary_a = format(a, "04b")  # 4-bit binary representation of a
        binary_b = format(b, "04b")  # 4-bit binary representation of b

        # Create Tex objects for the binary digits of a and b with correct indices
        bit_texts_a = [
            Tex(
                f"{bit}", color=(WIRE_COLOR_FALSE if int(bit) == 0 else WIRE_COLOR_TRUE)
            )
            for bit in binary_a
        ]
        bit_texts_a.reverse()
        bit_texts_b = [
            Tex(
                f"{bit}", color=(WIRE_COLOR_FALSE if int(bit) == 0 else WIRE_COLOR_TRUE)
            )
            for bit in binary_b
        ]
        bit_texts_b.reverse()

        # Arrange the bits next to the input gates
        for i, bit_text in enumerate(bit_texts_a):
            bit_text.move_to(manim_circuit.gates[f"input_a_{i}"]).shift(
                0.3 * UP + 0.05 * RIGHT
            )

        for i, bit_text in enumerate(bit_texts_b):
            bit_text.move_to(manim_circuit.gates[f"input_b_{i}"]).shift(
                0.3 * UP + 0.05 * RIGHT
            )

        # Group the bits for a and b
        bits_group_a = VGroup(*bit_texts_a)
        bits_group_b = VGroup(*bit_texts_b)

        # Animate the appearance of the bits
        anims = [FadeIn(bits_group_a), FadeIn(bits_group_b)]
        if fadeout_qms:
            anims += [FadeOut(questionmarks)]
        self.play(*anims)
        self.wait()

        a_tex = Tex(f"=\\,{a}", color=MAGENTA).next_to(bits_group_a, RIGHT, buff=1)
        b_tex = (
            Tex(f"=\\,{b}", color=MAGENTA)
            .next_to(bits_group_b, RIGHT, buff=1)
            .align_to(a_tex, LEFT)
        )

        self.play(Write(a_tex), Write(b_tex))
        self.wait()
        self.play(
            FadeOut(manim_circuits[3]),
            FadeIn(manim_circuits[4]),
            FadeOut(a_tex),
            FadeOut(b_tex),
            FadeOut(bits_group_a),
            FadeOut(bits_group_b),
            FadeOut(Group(*inp_c)),
            FadeOut(mult_tex),
            FadeOut(sat_group),
        )
        self.wait()

        c = 13
        number_c = (
            Tex(f"{c}", color=text_color)
            .scale(1.4)
            .next_to(eqs_c, DOWN, buff=0.5)
            .align_to(eqs_c, LEFT)
        )

        self.play(Write(number_c))
        self.wait()

        binary_c = (
            Tex(
                r"{{$ = \,$}}{{$0\, $}}{{$0\, $}}{{$0\, $}}{{$0\, $}}{{$1\, $}}{{$1\, $}}{{$0\, $}}{{$1\, $}}",
                color=text_color,
            )
            .scale(1.2)
            .next_to(number_c, RIGHT, buff=0.15)
        )

        for i in range(8):
            binary_c[8 - i].set_color(
                (WIRE_COLOR_FALSE if (c & (1 << i)) == 0 else WIRE_COLOR_TRUE)
            )

        self.play(Write(binary_c))
        self.wait()

        # Create animations to move each bit from binary_c to the corresponding position in eqs_c
        bit_animations = []
        for i in range(8):
            if i != 6:
                bit_animations.append(
                    ReplacementTransform(binary_c[i + 1], eqs_c[i][1])
                )
            else:
                bit_animations += [
                    binary_c[i + 1].animate.scale(TBL_SCALE).move_to(eqs_c[i][1]),
                    Transform(
                        eqs_c[i],
                        Tex(r"{{$x_{80}=\,$}}{{0}}", color=WIRE_COLOR_FALSE)
                        .scale(TBL_SCALE)
                        .move_to(eqs_c[i]),
                    ),
                ]

        # Play the animations
        self.play(*bit_animations, FadeOut(number_c), FadeOut(binary_c[0]))
        self.remove(binary_c[7])
        self.wait()

        # Create and display the SAT group
        sat_group.next_to(input_group, DOWN, buff=0.5)
        self.play(FadeIn(sat_group))
        self.wait()

        # Add text indicating that we're factoring 13
        factoring_tex = Tex(r"Factoring 13", color=text_color).next_to(
            sat_group, DOWN, buff=0.5
        )
        self.play(Write(factoring_tex))
        self.wait()

        # Add a large red tick mark
        tick_mark = (
            Text("×", color=RED)
            .scale_to_fit_height(1)
            .next_to(factoring_tex, RIGHT, buff=0.25)
        )
        self.play(Write(tick_mark))
        self.wait()


class Test(Scene):
    def construct(self):
        default()

        txt = Tex(r"Verifier", color=BLUE).set_z_index(20)
        rect = SurroundingRectangle(
            txt,
            color=text_color,
            fill_opacity=1,
            fill_color=BACKGROUND_COLOR,
        ).set_z_index(10)

        self.play(
            Create(rect),
            Write(txt),
        )
        self.wait()


class CircuitConversionScene(Scene):
    def construct(self):
        default()
        Tex = coltex
        CONSTRAINT_SCALE = 0.8

        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit, scale=2).to_edge(LEFT, buff=0.15)
        self.play(Create(manim_circuit, lag_ratio=0.02), run_time=1)
        self.wait()

        variables = Group(*[Tex(f"${c}$", color=text_color) for c in "abcdef"])
        variables[0].move_to(manim_circuit.gates[f"input_{0}"]).shift(
            0.5 * DR + 0.1 * DOWN + 0.2 * LEFT
        )
        variables[1].move_to(manim_circuit.gates[f"input_{1}"]).shift(
            0.3 * RIGHT + 0.4 * DOWN
        )
        variables[2].move_to(manim_circuit.gates[f"input_{2}"]).shift(
            0.3 * RIGHT + 2.3 * DOWN
        )

        variables[3].move_to(manim_circuit.gates[f"not_gate"]).shift(
            0.8 * DOWN + 0.25 * LEFT
        )

        variables[4].move_to(manim_circuit.gates[f"not_gate"]).shift(1.8 * DOWN)
        variables[5].move_to(manim_circuit.gates[f"output_{1}"]).shift(
            0.5 * UR + 0.1 * DOWN
        )

        self.play(
            AnimationGroup(
                *[FadeIn(var) for var in variables],
                lag_ratio=0.3,
            )
        )
        self.wait()

        rect = SurroundingRectangle(
            Group(variables[2], variables[4], variables[5]),
            color=RED,
        )
        self.play(Create(rect))
        self.wait()

        and_texs = VGroup(
            *[
                Tex(str, color=(text_color if i % 2 == 0 else GREEN)).scale(
                    CONSTRAINT_SCALE
                )
                for i, str in enumerate(
                    [
                        left_str
                        + not_str
                        + x3_str
                        + right_str
                        + or_str
                        + left_str
                        + not_str
                        + x5_str
                        + right_str
                        + or_str
                        + x6_str,
                        r"$\#\ \text{AND}(1,1) = 1$",
                        x3_str + or_str + left_str + not_str + x6_str + right_str,
                        r"$\#\ \text{AND}(0,\cdot) = 0$",
                        x5_str + or_str + left_str + not_str + x6_str + right_str,
                        r"$\#\ \text{AND}(\cdot ,0) = 0$",
                    ]
                )
            ]
        ).arrange_in_grid(cols=2, cell_alignment=LEFT, buff=0.25)

        or_texs = VGroup(
            *[
                Tex(str, color=(text_color if i % 2 == 0 else GREEN)).scale(
                    CONSTRAINT_SCALE
                )
                for i, str in enumerate(
                    [
                        x1_str
                        + or_str
                        + x4_str
                        + or_str
                        + left_str
                        + not_str
                        + x5_str
                        + right_str,
                        r"$\#\ \text{OR}(0, 0) = 0$",
                        left_str + not_str + x1_str + right_str + or_str + x5_str,
                        r"$\#\ \text{OR}(1,\cdot) = 1$",
                        left_str + not_str + x4_str + right_str + or_str + x5_str,
                        r"$\#\ \text{OR}(\cdot ,1) = 1$",
                    ]
                )
            ]
        ).arrange_in_grid(cols=2, cell_alignment=LEFT, buff=0.25)

        not_texs = VGroup(
            *[
                Tex(str, color=(text_color if i % 2 == 0 else GREEN)).scale(
                    CONSTRAINT_SCALE
                )
                for i, str in enumerate(
                    [
                        x2_str + or_str + x4_str,
                        r"$\#\  \text{NOT}(0) = 1$",
                        left_str
                        + not_str
                        + x2_str
                        + right_str
                        + or_str
                        + left_str
                        + not_str
                        + x4_str
                        + right_str,
                        r"$\#\  \text{NOT}(1) = 0$",
                    ]
                )
            ]
        )

        _all_texs = (
            VGroup(*not_texs, *or_texs, *and_texs)
            .arrange_in_grid(cols=2, cell_alignment=LEFT, buff=(0.5, 0.05))
            .next_to(manim_circuit, RIGHT, buff=1)
            .shift(0 * DOWN + 0.2 * RIGHT)
        )
        or_texs.shift(0.25 * UP)
        not_texs.shift(2 * 0.25 * UP)

        self.play(
            AnimationGroup(
                *[Write(submobjects_of(and_texs)[2 * i]) for i in range(3)],
                lag_ratio=0.5,
            )
        )
        self.wait()

        and_texs[0].save_state()
        sc = 1.3
        self.play(animate(and_texs[0]).scale(sc).shift(1 * UP + 2 * RIGHT))
        self.wait()

        shft = 0.05
        for j in [2, 7]:
            new_tex = (
                Tex(zero_str, color=WIRE_COLOR_FALSE)
                .scale(CONSTRAINT_SCALE * sc)
                .move_to(and_texs[0][j].get_center())
                .shift(shft * UP)
            )
            self.play(
                FadeOut(and_texs[0][j]),
                FadeIn(new_tex),
            )
            self.wait(0.5)
            self.play(
                FadeIn(and_texs[0][j]),
                FadeOut(new_tex),
            )
            self.wait()

        j1, j2 = 2, 7
        new_tex1 = (
            Tex(one_str, color=WIRE_COLOR_TRUE)
            .scale(CONSTRAINT_SCALE * sc)
            .move_to(and_texs[0][j1].get_center())
            .shift(shft * UP)
        )
        new_tex2 = (
            Tex(one_str, color=WIRE_COLOR_TRUE)
            .scale(CONSTRAINT_SCALE * sc)
            .move_to(and_texs[0][j2].get_center())
            .shift(shft * UP)
        )
        self.play(
            FadeOut(and_texs[0][j1]),
            FadeOut(and_texs[0][j2]),
            FadeIn(new_tex1),
            FadeIn(new_tex2),
        )
        self.wait()
        self.play(
            Transform(
                new_tex1,
                Tex(zero_str, color=WIRE_COLOR_FALSE)
                .scale(CONSTRAINT_SCALE * sc)
                .next_to(and_texs[0][4], LEFT, buff=0.15),
            ),
            Transform(
                new_tex2,
                Tex(zero_str, color=WIRE_COLOR_FALSE)
                .scale(CONSTRAINT_SCALE * sc)
                .next_to(and_texs[0][4], RIGHT, buff=0.15),
            ),
            FadeOut(and_texs[0][8]),
            animate(and_texs[0][9:])
            .next_to(and_texs[0][4], RIGHT, buff=0.55)
            .align_to(and_texs[0][4], UP),
            *[FadeOut(and_texs[0][jj]) for jj in [0, 1, 3, 5, 6]],
        )
        self.wait()

        self.play(
            FadeOut(new_tex1),
            FadeOut(new_tex2),
            *[FadeOut(and_texs[0][jj]) for jj in [4, 9, 10]],
            run_time=0.6,
        )
        and_texs[0].restore()
        self.play(
            FadeIn(and_texs[0]),
        )
        self.wait()
        self.play(
            Write(submobjects_of(and_texs)[1]),
        )
        self.wait()

        self.play(
            AnimationGroup(
                *[Write(submobjects_of(and_texs)[2 * i + 1]) for i in range(1, 3)],
                lag_ratio=0.5,
            )
        )
        self.wait()

        self.play(
            FadeOut(rect),
            FadeIn(or_texs),
            FadeIn(not_texs),
        )
        self.wait()


class InversionScene(Scene):
    def construct(self):
        default()
        self.next_section(skip_animations=False)

        circuit = make_multiplication_circuit(a=6, b=3).reverse()
        circuit.add_missing_inputs_and_outputs()
        manim_circuit = ManimCircuit(circuit, with_evaluation=True).scale(0.9)

        self.play(Create(manim_circuit, lag_ratio=0.002), run_time=3)
        self.wait()

        self.play(manim_circuit.animate_evaluation(scene=self, speed=1))
        self.wait()

        self.play(FadeOut(manim_circuit))
        self.wait()
        self.next_section(skip_animations=False)

        DOT_DISTANCE = 0.8
        left_dots = VGroup(*[Dot(color=text_color) for _ in range(5)]).arrange(
            DOWN, buff=DOT_DISTANCE
        )
        right_dots = VGroup(*[Dot(color=text_color) for _ in range(4)]).arrange(
            DOWN, buff=DOT_DISTANCE
        )
        fun_group = (
            VGroup(
                Tex(r"Circuit\\input", color=text_color),
                Tex(r"Circuit\\output", color=text_color),
                left_dots,
                right_dots,
            )
            .arrange_in_grid(cols=2, buff=0.5, col_widths=[4, 4])
            .to_edge(UP, buff=1)
        )

        for i in range(2):
            self.play(
                Write(submobjects_of(fun_group)[i]),
                AnimationGroup(
                    *[GrowFromCenter(dot) for dot in fun_group[i + 2]],
                    lag_ratio=0.5,
                ),
            )
            self.wait()

        forward_arrows = VGroup(
            *[
                Arrow(
                    start=left_dots[i].get_center(),
                    end=right_dots[j].get_center(),
                    color=BLUE,
                )
                for i, j in [(0, 3), (1, 0), (2, 3), (3, 2), (4, 3)]
            ]
        )

        self.play(
            AnimationGroup(
                *[GrowArrow(arrow) for arrow in submobjects_of(forward_arrows)],
                lag_ratio=0.5,
            )
        )
        self.wait()

        backward_arrows = VGroup(
            *[
                Arrow(
                    start=right_dots[i].get_center(),
                    end=left_dots[j].get_center(),
                    color=RED,
                ).shift(0.1 * UP)
                for i, j in [(0, 1), (2, 3), (3, 2)]
            ]
        )

        self.play(GrowArrow(submobjects_of(backward_arrows)[0]))
        tick_mark = (
            Text("×", color=RED).scale_to_fit_height(0.25).move_to(right_dots[1])
        )
        self.play(Write(tick_mark))
        self.play(GrowArrow(submobjects_of(backward_arrows)[1]))
        self.wait()

        circ = Circle(radius=0.25, color=RED).move_to(right_dots[3].get_center())
        self.play(Create(circ))
        self.wait()
        self.play(FadeOut(circ))
        self.play(GrowArrow(submobjects_of(backward_arrows)[2]))
        self.wait()


class CPUScene(Scene):
    def construct(self):
        default()
        algo_img = (
            ImageMobject("img/example_code.png")
            .scale_to_fit_width(4)
            .to_edge(LEFT, buff=1)
        )
        self.play(FadeIn(algo_img))
        self.wait()

        arrow = Arrow(
            start=algo_img.get_right(),
            end=algo_img.get_right() + 2 * RIGHT,
            color=text_color,
        )
        self.play(GrowArrow(arrow))
        self.wait()

        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit, scale=2).next_to(arrow, RIGHT, buff=0.5)
        self.play(Create(manim_circuit, lag_ratio=0.02), run_time=1)
        self.wait()

        cpu_img = ImageMobject("img/8008.jpg").scale_to_fit_width(config.frame_width)
        self.play(FadeIn(cpu_img))
        self.clear()
        self.add(cpu_img)
        self.wait()
        self.play(FadeOut(cpu_img))
        self.wait()

        circuit = make_example_circuit()
        manim_circuit = ManimCircuit(circuit, scale=2).shift(2 * RIGHT)
        self.play(Create(manim_circuit, lag_ratio=0.02), run_time=1)
        self.wait()

        input_tex = Tex(r"Input", color=text_color).next_to(
            manim_circuit.gates["input_0"], LEFT, buff=2
        )
        output_tex = Tex(r"Output", color=text_color).next_to(
            manim_circuit.gates["output_0"], LEFT, buff=2
        )
        output_tex.shift((center_of(input_tex) - center_of(output_tex))[0] * RIGHT)
        arrow = Arrow(
            start=input_tex.get_bottom(),
            end=output_tex.get_top(),
            color=text_color,
        )

        self.play(
            Succession(
                Write(input_tex),
                Write(output_tex),
            )
        )
        self.wait()

        question_1 = (
            Tex(
                "``If I run the algorithm on a given input, what output do I get?''",
                color=BLUE,
            )
            .shift(3 * UP)
            .scale(0.8)
        )

        self.play(Write(question_1))

        self.play(
            Succession(
                GrowArrow(arrow),
                Indicate(input_tex, color=text_color),
                Indicate(output_tex, color=text_color),
            )
        )
        self.wait()

        question_2 = (
            Tex(
                "``If I want to arrive at a given output, "
                "what input do I have to start with?''",
                color=BLUE,
            )
            .shift(3 * UP)
            .scale(0.8)
        )

        self.play(
            Rotate(arrow, angle=PI, about_point=list(arrow.get_center())),
            animate(question_1).become(question_2),
        )
        self.play(Indicate(output_tex, color=text_color))
        self.play(Indicate(input_tex, color=text_color))

        self.wait()
