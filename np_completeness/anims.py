# type: ignore[reportArgumentType]
# manim -pql --disable_caching --fps 15 -r 290,180 anims.py Polylogo
from manim import *

from np_completeness.utils.util_general import *

# from utils.util_general import *

CROWN_BUFF = 0.1
CROWN_SCALE = 0.25
BOX_COLOR = BASE3



class Polylogo(Scene):
    def construct(self):
        default()
        authors = Tex(
            r"\textbf{Richard Hladík, Filip Hlásek, Václav Rozhoň, Václav Volhejn}",
            color=text_color,
            font_size=40,
        ).shift(3 * DOWN + 0 * LEFT)

        channel_name = Tex(r"polylog", color=text_color)
        channel_name.scale(4).shift(1 * UP)
        channel_name_without_o = Tex(r"p\hskip 5.28pt lylog", color=text_color)
        channel_name_without_o.scale(4).shift(1 * UP)

        logo_solarized = (
            SVGMobject("img/logo-solarized.svg")
            .scale(0.55)
            .move_to(2 * LEFT + 0.95 * UP + 0.49 * RIGHT)
        )
        self.play(
            Write(authors),
            Write(channel_name),
        )
        self.play(FadeIn(logo_solarized))
        self.add(channel_name_without_o)
        self.remove(channel_name)

        self.wait()

        self.play(*[FadeOut(o) for o in self.mobjects])
        self.wait()


class IntroSAT(Scene):
    def construct(self):
        default()

        header_tex = Tex(r"Satisfiability (SAT)").scale(1.5).to_edge(UP)
        self.play(Write(header_tex))
        self.wait()

        # The story of P vs NP is the story of the satisfiability problem, also known as SAT. In this problem, we are given an input that looks like this.


        variables = Group(
            Tex(r"Variables:"),
            *[
                Tex(str)
                for str in [
                    x1_str + eq_str + true_str,
                    x2_str + eq_str + false_str,
                    x3_str + eq_str + false_str,
                    x4_str + eq_str + true_str,
                ]
            ],
        ).arrange_in_grid(cols=1, cell_alignment=LEFT)

        constraints = Group(
            Tex(r"Constraints:"),
            *[
                Tex(str)
                for str in [
                    x1_str + or_str + left_str + not_str + x3_str + right_str,
                    not_str + x2_str,
                    x2_str
                    + or_str
                    + left_str
                    + not_str
                    + x3_str
                    + right_str
                    + or_str
                    + left_str
                    + not_str
                    + x4_str
                    + right_str,
                ]
            ],
        ).arrange_in_grid(cols=1, cell_alignment=LEFT)

        SIMPLIFIED_SCALE = 1
        plugged_constraints = Group(
            *[
                Tex(str).scale(SIMPLIFIED_SCALE)
                for str in [
                    one_str + or_str + left_str + not_str + zero_str + right_str,
                    not_str + zero_str,
                    zero_str
                    + or_str
                    + left_str
                    + not_str
                    + zero_str
                    + right_str
                    + or_str
                    + left_str
                    + not_str
                    + one_str
                    + right_str,
                ]
            ]
        )

        simplified_constraints = Group(
            *[
                Tex(str).scale(SIMPLIFIED_SCALE)
                for str in [
                    one_str + or_str + one_str,
                    one_str,
                    zero_str + or_str + one_str + or_str + zero_str,
                ]
            ]
        )

        vc = Group(variables, constraints).arrange_in_grid(
            cols=2, cell_alignment=UL, buff=2
        )
        constraints[1:].shift(0.5 * DOWN)
        for i in range(3):
            for c in [plugged_constraints[i], simplified_constraints[i]]:
                c.move_to(constraints[i + 1]).align_to(constraints[i + 1], LEFT)
            if i == 0 or i == 2:
                simplified_constraints[i].shift(
                    plugged_constraints[i][1].get_center()
                    - simplified_constraints[i][1].get_center()
                )

        self.play(
            AnimationGroup(
                Write(variables[0]),
                *[Write(v[0]) for v in variables[1:]],
                lag_ratio=0.5,
            )
        )
        self.wait()

        self.play(AnimationGroup(*[Write(v[1:]) for v in variables[1:]], lag_ratio=0.5))
        self.wait()

        # l = 1
        # for i in range(l):
        #     if i < l - 1:
        #         self.play(
        #             *[
        #                 Transform(
        #                     v[2],
        #                     Tex(
        #                         (true_str if random.randint(0, 1) == 0 else false_str)
        #                     ).move_to(v[2]),
        #                 )
        #                 for v in variables[1:]
        #             ]
        #         )
        #     else:
        #         final_vals = [true_str, false_str, false_str, true_str]
        #         self.play(
        #             AnimationGroup(*[
        #                 Transform(v[2], Tex(val).move_to(v[2]))
        #                 for v, val in zip(variables[1:], final_vals)
        #             ],
        #             lag_ratio=0.5)
        #         )
        #     self.wait(0.5)
        # self.wait(0.5)

        # change true/false to 1/0
        self.play(
            *[
                Transform(v[2], Tex(str(val), color = text_color).next_to(v[1], RIGHT, buff = 0.2))
                for val, v in zip([1,0,0,1], variables[1:])
            ]
        )
        self.wait()

        self.play(*[FadeOut(v[1:]) for v in variables[1:]])
        self.play(AnimationGroup(*[Write(c) for c in constraints], lag_ratio=0.5))
        self.wait()

        crazy_formula_tex = Tex(
            r"$(x_1 \rightarrow (\text{NOT}\, x_3)) \leftrightarrow ((x_2 \,\text{NAND}\, x_3) \,\text{XOR}\, x_4)  $"
        ).to_edge(DOWN, buff=1.3)
        self.play(
            Write(crazy_formula_tex),
        )
        self.wait()
        self.play(
            FadeOut(crazy_formula_tex),
        )

        cnf_sat_tex = Tex(r"CNF-SAT").scale(1.25).to_edge(DOWN, buff=1.3)
        arrow = Arrow(
            cnf_sat_tex.get_right(), constraints[-1].get_bottom(), color=text_color
        )
        self.play(
            Write(cnf_sat_tex),
            Create(arrow),
        )
        self.wait()
        self.play(
            FadeOut(cnf_sat_tex),
            FadeOut(arrow),
        )
        self.wait()

        rects = [
            SurroundingRectangle(tx, color=RED)
            for tx in [
                constraints[1][0],
                constraints[1][4],
                constraints[2][1],
                constraints[3][0],
                constraints[3][4],
                constraints[3][9],
            ]
        ]

        self.play(
            *[Create(rect) for rect in rects],
        )
        self.wait()

        self.play(
            Transform(rects[1], SurroundingRectangle(constraints[1][2:], color=RED)),
            Transform(rects[2], SurroundingRectangle(constraints[2], color=RED)),
            Transform(rects[4], SurroundingRectangle(constraints[3][2:6], color=RED)),
            Transform(rects[5], SurroundingRectangle(constraints[3][7:], color=RED)),
        )
        self.wait()

        ors = [constraints[1][1], constraints[3][1], constraints[3][6]]
        self.play(
            *[Indicate(or_, color=BLUE) for or_ in ors],
        )
        self.wait()

        self.play(FadeOut(Group(*rects)))
        self.wait()

        constraints[3].save_state()
        self.play(
            constraints[3].animate.scale(1.5).to_edge(DOWN, buff=2).shift(1 * LEFT)
        )
        self.wait()

        rec = SurroundingRectangle(constraints[3][0], color=RED)
        self.play(Create(rec))
        self.wait()
        self.play(Transform(rec, SurroundingRectangle(constraints[3][2:6], color=RED)))
        self.wait()
        self.play(Transform(rec, SurroundingRectangle(constraints[3][7:], color=RED)))
        self.wait()
        self.play(FadeOut(rec), constraints[3].animate.restore())
        self.wait()

        # for i, str in enumerate([true_str, false_str, false_str, true_str]):
        #     variables[i+1][2] = Tex(str).next_to(variables[i+1][1], RIGHT)
        self.next_section(skip_animations=False)

        self.play(
            AnimationGroup(
                *[FadeIn(variable[1:]) for variable in variables[1:]], lag_ratio=0.5
            )
        )
        self.wait()

        copies = []
        for i, k, l in [
            (1, 0, 0),
            (3, 0, 4),
            (2, 1, 1),
            (2, 2, 0),
            (3, 2, 4),
            (4, 2, 9),
        ]:
            copy = variables[i][2].copy()
            copy.generate_target()
            copy.target.scale(SIMPLIFIED_SCALE).move_to(plugged_constraints[k][l])
            copies.append(copy)

        self.play(
            *[
                Transform(constraint, plugged_constraint)
                for constraint, plugged_constraint in zip(
                    constraints[1:], plugged_constraints
                )
            ],
            *[MoveToTarget(copy) for copy in copies],
        )
        self.wait()

        self.remove(*copies)
        self.play(
            Transform(constraints[1][2:], simplified_constraints[0][2]),
            Transform(constraints[2], simplified_constraints[1]),
            Transform(constraints[3][2:6], simplified_constraints[2][2]),
            Transform(constraints[3][6], simplified_constraints[2][3]),
            Transform(constraints[3][7:], simplified_constraints[2][4]),
        )
        self.wait()

        # self.play(
        #     *[
        #         Create(SurroundingRectangle(c, color=RED))
        #         for c in [
        #             simplified_constraints[0][0],
        #             simplified_constraints[1][0],
        #             simplified_constraints[2][2],
        #         ]
        #     ],
        # )
        # self.wait()

        self.play(
            *[
                Transform(constraint, Tex(r"1").move_to(constraint).align_to(constraint, LEFT))
                for constraint in constraints[1:]
            ]
        )
        self.wait()


class BreakRSA(Scene):
    def construct(self):
        default()
        texts = [
            Tex(r"Breaking RSA \\ (factoring numbers of size $10^{500}$)"),
            Tex(r"$\Downarrow$ our reduction"),
            Tex(r"Solving SAT with $\sim50$M variables"),
            # MathTex(r"\Rightarrow"),
        ]
        g = Group(*texts).arrange(DOWN, buff=1)
        self.play(LaggedStart(*[Write(t) for t in texts], lag_ratio=0.8))
        self.wait()
