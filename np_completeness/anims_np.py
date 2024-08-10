# type: ignore[reportArgumentType]
# manim -pql --disable_caching --fps 15 -r 290,180 anims.py Polylogo
from manim import *

from np_completeness.utils.util_general import *

# from utils.util_general import *

CROWN_BUFF = 0.1
CROWN_SCALE = 0.25
BOX_COLOR = BASE3


class NP(Scene):
    def construct(self):
        default()

        # The theoretical definition of a fast algorithm is that its time complexity is a polynomial function.
        fast_text = Tex("fast")
        equals = Tex("=")
        polynomial_time = Tex("polynomial-time")

        fast_def = VGroup(fast_text, equals, polynomial_time).arrange(RIGHT)

        self.play(Write(fast_text))
        self.wait()
        self.play(Write(equals))
        self.wait()
        self.play(Write(polynomial_time))
        self.wait()

        self.play(FadeOut(fast_def))

        # The class of all problems where you can verify proposed solutions in polynomial time is called NP and it contains most important computer science problems including coloring, factoring, or much simpler problems like multiplying two numbers.
        np_rect = Rectangle(
            width=7, height=5, color=text_color, fill_opacity=0.5, fill_color=BOX_COLOR
        ).to_edge(LEFT, buff=2)
        np_label = (
            Tex(r"\raggedright NP = verification \\ in polynomial time")
            .next_to(np_rect, RIGHT)
            .align_to(np_rect, UP)
        )

        problems = ["SATISFIABILITY", "COLORING", "FACTORING", "MULTIPLICATION"]
        problem_texs = [Tex(problem) for problem in problems]
        problem_rects = Group(
            *[
                Group(
                    SurroundingRectangle(
                        tex,
                        color=text_color,
                        fill_opacity=1,
                        fill_color=BACKGROUND_COLOR,
                    ),
                    tex,
                )
                for tex in problem_texs
            ]
        )

        for rect, tex in problem_rects:
            rect.set_z_index(10)
            tex.set_z_index(20)

        problem_rects[0].next_to(np_rect, UP, buff=0.3)
        problem_rects[1:].arrange(DOWN).move_to(np_rect.get_center()).shift(0.5 * DOWN)
        problem_rects[1].shift(1.5 * LEFT)
        problem_rects[2].shift(0.2 * RIGHT + 0.25 * DOWN)
        problem_rects[3].shift(1 * RIGHT + 0.5 * DOWN)

        self.play(Create(np_rect), Write(np_label))
        for rect in problem_rects[1:]:
            self.play(Write(rect[0]), Create(rect[1]))
        self.wait()

        self.play(Write(problem_rects[0][0]), Create(problem_rects[0][1]))
        self.wait()

        shifts = [1 * LEFT, 0 * LEFT, 1 * RIGHT]
        # Our trick with converting algorithms to SAT problems works in polynomial time.
        arrows = []
        for i in range(3):
            start = problem_rects[i + 1].get_top()
            end = problem_rects[0].get_bottom() + shifts[i]
            arrow = Arrow(start=start, end=end, buff=0.1)  # Added a small buffer
            arrows.append(arrow)
        arrows = VGroup(*arrows)

        self.play(*[GrowArrow(arrow) for arrow in arrows])
        self.wait()

        # This means that a SAT solver that runs in polynomial time would imply polynomial-time solution for *any* problem in NP.
        poly_labels = VGroup(
            *[
                Tex("polynomial", color=BLUE, font_size=30)
                .next_to(rect, UP, buff=0.1)
                .align_to(rect, RIGHT)
                for rect in problem_rects
            ]
        )
        self.play(Write(poly_labels[0]))
        self.play(
            *[
                ReplacementTransform(poly_labels[0].copy(), label)
                for label in poly_labels[1:]
            ]
        )
        self.wait()

        self.play(
            *[FadeOut(obj) for obj in poly_labels],
        )
        self.wait()

        # But here's a fun fact: The satisfiability problem is *itself *in the class NP.
        problem_rects[0].generate_target()
        problem_rects[0].target.align_to(np_rect, UP).shift(0.75 * DOWN)

        self.play(
            MoveToTarget(problem_rects[0]),
            *[
                ar.animate.put_start_and_end_on(
                    ar.get_start(), problem_rects[0].target.get_bottom() + shifts[i]
                )
                for i, ar in enumerate(arrows)
            ],
        )
        self.wait()

        crown = (
            SVGMobject("img/crown.svg")
            .scale(CROWN_SCALE)
            .next_to(problem_rects[0], UP, buff=CROWN_BUFF)
            .set_color(text_color)
        )

        self.play(FadeIn(crown))
        self.wait()


class NP2(Scene):
    def construct(self):
        default()

        npc_tex = Tex(
            r"{{\raggedright A problem is }}{{NP-complete}}{{ if: \\}}{{ 1. It is in NP.  \\}}{{ 2. Every problem in NP is reducible to it \\ \;\;\;\; in polynomial time. (=NP-hard) }}"
        )
        crown = (
            SVGMobject("img/crown.svg")
            .scale(CROWN_SCALE)
            .set_color(text_color)
            .next_to(npc_tex[1], UP, buff=CROWN_BUFF)
        )
        self.play(
            AnimationGroup(
                Write(npc_tex[0:3]),
                FadeIn(crown),
                lag_ratio=0.5,
            )
        )
        self.wait(0.5)
        self.play(Write(npc_tex[3]))
        self.wait(0.5)
        self.play(Write(npc_tex[4]))

        self.wait()
        self.play(
            FadeOut(npc_tex),
            FadeOut(crown),
        )
        self.wait()

        thm_tex = (
            Tex(r"{{SATISFIABILITY}}{{ is }}{{NP-complete. }}")
            .scale(1.5)
            .to_edge(UP, buff=1)
        )
        crown = (
            SVGMobject("img/crown.svg")
            .scale(CROWN_SCALE * 1.5)
            .set_color(text_color)
            .next_to(thm_tex[2], UP, buff=CROWN_BUFF * 1.5)
        )
        self.play(
            AnimationGroup(
                Write(thm_tex),
                FadeIn(crown),
                lag_ratio=0.5,
            )
        )
        self.wait()

        images = (
            Group(
                *[
                    Group(
                        ImageMobject(path).scale_to_fit_height(3.5), Tex(name)
                    ).arrange(DOWN)
                    for path, name in [
                        ("img/cook.webp", "Stephen Cook"),
                        ("img/levin.jpeg", "Leonid Levin"),
                    ]
                ]
            )
            .arrange(RIGHT, buff=1, aligned_edge=UP)
            .shift(0.5 * DOWN + 1.5 * LEFT)
        )

        self.play(FadeIn(images[0]))
        self.play(FadeIn(images[1]))
        self.wait()

        thumb = ImageMobject("img/thumbnail2.png").scale_to_fit_width(4).to_edge(RIGHT)
        rec = SurroundingRectangle(thumb, color=text_color)
        thumb = Group(thumb, rec)

        self.play(FadeIn(thumb))
        self.wait()

        self.play(
            *[FadeOut(o) for o in images],
            FadeOut(thumb),
            FadeOut(thm_tex[1:]),
            FadeOut(crown),
        )
        self.wait(2)


class NP3(MovingCameraScene):
    def construct(self):
        default()
        self.camera.frame.save_state()

        thm_tex = (
            Tex(r"{{SATISFIABILITY}}{{ is NP-complete. }}", z_index=100)
            .scale(1.5)
            .to_edge(UP, buff=1)
        )
        self.add(thm_tex[0])

        karp_img = (
            Group(
                ImageMobject("img/karp.jpeg").scale_to_fit_height(3.5),
                Tex("Richard Karp"),
            )
            .arrange(DOWN)
            .to_edge(RIGHT)
        )

        self.play(FadeIn(karp_img))
        self.wait()

        num_karp_problems = 8
        problems_data = [
            ("SATISFIABILITY", ("SATISFIABILITY", ORIGIN), None, None, None, -1),
            (
                "COLORING",
                ("SATISFIABILITY", 2 * UL + 0 * DOWN + 1.5 * LEFT),
                "SATISFIABILITY",
                UP,
                DOWN,
                0,
            ),
            (
                "TRAVELLING SALESMAN",
                ("SATISFIABILITY", 2 * UR + 0.5 * UP),
                "SATISFIABILITY",
                UP,
                DOWN,
                1,
            ),
            (
                "MAX CLIQUE",
                ("SATISFIABILITY", 2 * DR + 1 * RIGHT + 1 * DOWN + 1 * LEFT),
                "SATISFIABILITY",
                DOWN,
                UP,
                0,
            ),
            (
                "INTEGER PROGRAMMING",
                ("SATISFIABILITY", 2 * DL + 1 * LEFT),
                "SATISFIABILITY",
                DOWN,
                UP,
                1,
            ),
            ("MAX CUT", ("SATISFIABILITY", 5 * LEFT + 4 * UP), "COLORING", UP, DOWN, 0),
            (
                "KNAPSACK",
                ("SATISFIABILITY", 1 * LEFT + 4 * UP),
                "COLORING",
                UP,
                DOWN,
                1,
            ),
            (
                "VERTEX COVER",
                ("MAX CLIQUE", 5 * LEFT + 0.5 * DOWN),
                "MAX CLIQUE",
                LEFT,
                RIGHT,
                0,
            ),
            ("k-MEANS", ("COLORING", 4 * LEFT + 1 * DOWN), "COLORING", LEFT, RIGHT, 2),
            (
                "JOB SCHEDULING",
                ("KNAPSACK", 2 * UP + 1 * LEFT),
                "KNAPSACK",
                UP,
                DOWN,
                1,
            ),
            ("MINESWEEPER", ("KNAPSACK", 2 * UP + 6 * RIGHT), "KNAPSACK", UP, DOWN, 4),
            (
                "VEHICLE ROUTING",
                ("TRAVELLING SALESMAN", 5 * RIGHT + 2 * UP),
                "TRAVELLING SALESMAN",
                UP,
                DOWN,
                1,
            ),
            (
                "PROTEIN FOLDING",
                ("SATISFIABILITY", 8 * RIGHT + 2 * UP),
                "SATISFIABILITY",
                RIGHT,
                LEFT,
                3,
            ),
            (
                "MULTI-COMMODITY FLOW",
                ("SATISFIABILITY", 7 * RIGHT + 0.5 * UP),
                "SATISFIABILITY",
                RIGHT,
                LEFT,
                1,
            ),
            (
                "TETRIS",
                ("SATISFIABILITY", 7 * RIGHT - 1 * UP),
                "SATISFIABILITY",
                RIGHT,
                LEFT,
                4,
            ),
            (
                "CANDYCRUSH",
                ("SATISFIABILITY", 6.5 * RIGHT - 2.5 * UP),
                "SATISFIABILITY",
                RIGHT,
                LEFT,
                4,
            ),
            ("TRAINING SVM", ("MAX CLIQUE", 2 * DOWN), "MAX CLIQUE", DOWN, UP, 2),
            (
                "TRAINING NEURAL NETS",
                ("SATISFIABILITY", 7 * LEFT + 1 * DOWN),
                "SATISFIABILITY",
                LEFT,
                RIGHT,
                2,
            ),
            (
                "MULTIPLE SEQUENCE ALIGNMENT",
                ("VERTEX COVER", 3 * LEFT + 2 * DOWN),
                "VERTEX COVER",
                DOWN,
                UP,
                3,
            ),
        ]

        problems = []
        crowns = []
        arrows = []

        for i, (
            name,
            (ref_problem, position),
            arrow_from,
            arrow_start,
            arrow_end,
            problem_type,
        ) in enumerate(problems_data):
            tex = Tex(name).set_z_index(5)
            rect = SurroundingRectangle(
                tex, color=text_color, fill_color=BACKGROUND_COLOR, z_index=1
            )
            problem = VGroup(rect, tex)

            if i == 0:
                problem[1].scale(1.5)
                problem.move_to(position)
            else:
                ref = next(p for p in problems if p[1].tex_string == ref_problem)
                problem.move_to(ref.get_center() + position)

            problems.append(problem)
            crowns.append(
                SVGMobject("img/crown.svg")
                .scale(CROWN_SCALE)
                .set_color(BASE01)
                .next_to(problem, UP, buff=CROWN_BUFF)
            )

            if arrow_from:
                from_problem = next(
                    p for p in problems if p[1].tex_string == arrow_from
                )
                start = from_problem[0].get_edge_center(arrow_start)
                end = problem.get_edge_center(arrow_end)
                arrows.append(Arrow(start=start, end=end, buff=0.1, color=BASE1))

        # Animation code
        problems[0][1].move_to(thm_tex[0])
        self.remove(thm_tex[0])
        self.play(
            Create(problems[0][0]),
            problems[0][1].animate.scale(1 / 1.5).move_to(problems[0][0].get_center()),
        )
        self.play(FadeIn(crowns[0]))
        self.wait()

        self.play(
            AnimationGroup(
                *[
                    AnimationGroup(Create(p[0]), Write(p[1]))
                    for p in problems[1:num_karp_problems]
                ],
                lag_ratio=0.5,
            ),
            self.camera.frame.animate(run_time=6).move_to(ORIGIN).set(width=18),
        )
        self.wait()

        self.play(
            AnimationGroup(
                *[FadeIn(c) for c in crowns[1:num_karp_problems]], lag_ratio=0.3
            )
        )
        self.wait()

        self.play(
            AnimationGroup(
                *[GrowArrow(a) for a in arrows[: num_karp_problems - 1]], lag_ratio=0.5
            ),
        )
        self.wait()

        self.play(
            FadeOut(karp_img),
        )

        self.wait()

        self.play(
            AnimationGroup(
                *[
                    AnimationGroup(
                        FadeIn(crowns[i]),
                        Write(problems[i][1]),
                        Create(problems[i][0]),
                        GrowArrow(arrows[i - 1]),
                    )
                    for i in range(num_karp_problems, len(problems))
                ],
                lag_ratio=0.5,
            ),
            self.camera.frame.animate(run_time=4)
            .move_to(ORIGIN + 0.5 * DOWN)
            .set(width=28),
        )
        self.wait()

        problem_types = [
            "Graph Theory",
            "Optimization",
            "Machine Learning",
            "Bioinformatics",
            "Games",
        ]
        for type_index, type_name in enumerate(problem_types):
            type_problems = [
                p
                for p, (_, _, _, _, _, t) in zip(problems, problems_data)
                if t == type_index
            ]

            for p in type_problems:
                p[0].set_z_index(-5)
                p.save_state()

            self.play(
                *[p[0].animate.set_fill(BASE02, opacity=1) for p in type_problems],
                *[p[1].animate.set_color(BASE3) for p in type_problems],
                run_time=1,
            )

            type_text = (
                Tex(type_name, color=BASE02)
                .scale(2)
                .align_to(self.camera.frame.get_corner(UL), UL)
                .shift(0.5 * DR)
            )
            self.play(Write(type_text))

            self.wait(2)

            self.play(
                *[p.animate.restore() for p in type_problems],
                FadeOut(type_text),
                run_time=1,
            )

        minesweeper_problem = next(
            p for p in problems if p[1].tex_string == "MINESWEEPER"
        )

        polynomial_text = (
            Tex("polynomial", color=BLUE)
            .next_to(minesweeper_problem, UP, buff=0.2)
            .align_to(minesweeper_problem, RIGHT)
        )

        polynomial_text.save_state()
        polynomial_text.scale(4).align_to(self.camera.frame.get_corner(UR), UR).shift(
            0.5 * DL
        )

        self.play(polynomial_text.animate.restore())
        self.wait(1)

        polynomial_copies = []
        for problem in problems:
            if problem != minesweeper_problem:
                copy = polynomial_text.copy()
                copy.next_to(problem, UP, buff=0.2).align_to(problem, RIGHT)
                polynomial_copies.append(copy)

        self.play(
            *[TransformFromCopy(polynomial_text, copy) for copy in polynomial_copies],
            run_time=2,
        )
        self.wait()

        self.play(
            FadeOut(polynomial_text),
            *[FadeOut(copy) for copy in polynomial_copies],
            run_time=1,
        )

        # Move all problems to the center
        target_positions = []
        radius = 2  # Adjust this value to change how spread out the problems are
        for i, problem in enumerate(problems):
            angle = i * (2 * PI / len(problems))
            target_position = radius * (np.cos(angle) * RIGHT + np.sin(angle) * UP)
            target_positions.append(target_position)

        # Create new central SATISFIABILITY box
        big_sc = 3
        central_sat = Tex("SATISFIABILITY", color=text_color).scale(big_sc)
        central_rect = SurroundingRectangle(
            central_sat, color=text_color, fill_color=BACKGROUND_COLOR, fill_opacity=1
        )
        central_problem = Group(central_rect, central_sat).set_z_index(10)

        self.play(
            *[FadeOut(arrow) for arrow in arrows],
            *[FadeOut(crown) for crown in crowns[1:]],
            crowns[0]
            .animate.scale(big_sc)
            .next_to(central_problem, buff=CROWN_BUFF * big_sc, direction=UP),
            *[
                problem.animate.move_to(pos)
                for problem, pos in zip(problems, target_positions)
            ],
            # self.camera.frame.animate.scale(0.6).move_to(ORIGIN),  # Zoom in
            self.camera.frame.animate.move_to(ORIGIN).set(width=14),
            run_time=2,
        )

        self.play(
            FadeIn(central_problem[0]),
            Write(central_problem[1]),
        )

        self.play(
            *[FadeOut(problem) for problem in problems],
        )

        self.wait(2)


class NP4(MovingCameraScene):
    def construct(self):
        default()
        self.camera.frame.move_to(ORIGIN).set(width=14)

        big_sc = 3
        central_sat = Tex("SATISFIABILITY", color=text_color)
        central_rect = SurroundingRectangle(
            central_sat, color=text_color, fill_color=BACKGROUND_COLOR, fill_opacity=1
        )
        central_problem = VGroup(central_rect, central_sat).set_z_index(10)
        crown = (
            SVGMobject("img/crown.svg")
            .scale(CROWN_SCALE)
            .set_color(text_color)
            .next_to(central_problem, UP, buff=CROWN_BUFF)
        )
        self.add(central_problem, crown)

        VGroup(central_problem, crown).scale(big_sc)

        self.play(Group(central_problem, crown).animate.scale(1 / big_sc).shift(1 * UP))
        self.wait()

        problem_names = [
            "MULTIPLICATION",
            "SORTING",
            "FACTORING",
            "FINDING A WINNING STRATEGY",
        ]
        problem_texs = [Tex(problem) for problem in problem_names]
        problems = Group(
            *[
                Group(
                    SurroundingRectangle(
                        tex,
                        color=text_color,
                        fill_opacity=1,
                        fill_color=BACKGROUND_COLOR,
                    ),
                    tex,
                )
                for tex in problem_texs
            ]
        )

        for i, (rect, tex) in enumerate(problems):
            rect.set_z_index(10 + 2 * i)
            tex.set_z_index(10 + 2 * i + 1)

        problems[0].move_to(2 * DOWN + 1 * LEFT)
        problems[1].move_to(1 * DOWN + 1 * RIGHT)
        problems[2].move_to(-0.5 * DOWN + 0 * LEFT)
        problems[3].move_to(3.5 * UP)

        self.play(
            AnimationGroup(
                *[AnimationGroup(Create(p[0]), Write(p[1])) for p in problems[:2]],
                lag_ratio=0.5,
            )
        )
        self.wait()

        p_box = SurroundingRectangle(
            problems[:2], color=text_color, fill_opacity=0.5, fill_color=GREEN
        )
        p_tex = (
            Tex(
                r"{{\raggedright P}}{{ = solvable \\ in polynomial time}}",
                color=text_color,
            )
            .next_to(p_box, RIGHT)
            .align_to(p_box, UP)
        )

        self.play(Create(p_box), Write(p_tex))
        self.wait()

        np_tex = (
            Tex(r"\raggedright NP-complete", color=text_color)
            .next_to(central_sat, RIGHT)
            .align_to(p_tex, LEFT)
        )
        self.play(Write(np_tex))
        self.wait()

        # factoring
        self.play(
            Create(problems[2][0]),
            Write(problems[2][1]),
        )

        for i in range(2):
            problems[2][i].save_state()

        self.play(problems[2].animate.align_to(p_box, UL).shift(0.2 * DR))
        self.wait()

        self.play(problems[2].animate.next_to(crown, LEFT, buff=0.1))
        self.wait()
        self.play(*[problems[2][i].animate.restore() for i in range(2)])
        self.wait()

        # final problem

        chess_img = ImageMobject("img/chess.jpg", z_index=100).scale_to_fit_width(10)
        self.play(FadeIn(chess_img))
        self.play(
            AnimationGroup(
                chess_img.animate.scale(0).move_to(problems[3].get_center()),
                AnimationGroup(
                    Create(problems[3][0]),
                    Write(problems[3][1]),
                ),
                lag_ratio=0.5,
            )
        )
        self.remove(chess_img)
        self.wait()

        self.play(
            *[FadeOut(problem) for problem in problems[2:]],
            FadeOut(p_tex[1]),
            p_tex[0].animate.next_to(p_box, RIGHT, buff=1),
            np_tex.animate.shift(1 * RIGHT),
        )
        self.wait()

        self.wait()

        # sat goes down

        for o in [central_problem[0], central_problem[1], crown, p_box]:
            o.save_state()

        sat = Group(central_problem, crown)
        sat.generate_target()
        sat.target.align_to(problems[1], UP).shift(1.5 * UP)
        sat_pos = sat.get_center()

        self.play(
            MoveToTarget(sat),
            FadeOut(np_tex),
            Transform(
                p_box,
                SurroundingRectangle(
                    Group(problems[0], problems[1], sat.target),
                    color=text_color,
                    fill_opacity=0.5,
                    fill_color=GREEN,
                ),
            ),
        )
        self.wait()

        self.play(
            sat.animate.move_to(sat_pos),
            Transform(
                p_box,
                SurroundingRectangle(
                    Group(problems[0], problems[1]),
                    color=text_color,
                    fill_opacity=0.5,
                    fill_color=GREEN,
                ),
            ),
        )
        self.wait()

        np_box = SurroundingRectangle(
            Group(sat, p_box), color=text_color, fill_opacity=0.5, fill_color=RED
        ).set_z_index(-1)
        np_tex = (
            Tex(r"{{\raggedright NP}}", color=text_color)
            .next_to(np_box, RIGHT)
            .align_to(np_box, UP)
        )

        self.play(
            Create(np_box),
            Write(np_tex),
        )
        self.wait()

        sat.generate_target()
        sat.target.align_to(problems[1], UP).shift(1.5 * UP)

        self.play(
            MoveToTarget(sat),
            *[
                Transform(
                    box,
                    SurroundingRectangle(
                        Group(problems[0], problems[1], sat.target),
                        color=text_color,
                        fill_opacity=0.5,
                        fill_color=GREEN,
                    ),
                )
                for box in [p_box, np_box]
            ],
            Transform(
                p_tex[0],
                Tex(r"P = NP?", color=text_color).next_to(p_box, RIGHT).shift(1 * UR),
            ),
            FadeOut(np_tex),
        )
        self.wait()


class SATJoke(Scene):
    def construct(self):
        default()
        # Quote
        quote = (
            Text(
                "I can't get no satisfaction\n'Cause I try\nand I try\nand I try\nand I try",
                slant=ITALIC,
            )
            .scale(0.8)
            .shift(0.5 * UP + 2 * LEFT)
        )
        # quote = Tex(r"{{I can't get no satisfaction\\}}{{'Cause I try\\}}{{and I try\\}}{{and I try\\}}{{and I try}}",
        #             color=text_color, slant=ITALIC).scale(0.8).next_to(main_text, DOWN, buff=0.5)

        # Images
        jagger_img = ImageMobject("img/jagger.jpg").scale_to_fit_height(3)
        richards_img = ImageMobject("img/richards.jpg").scale_to_fit_height(3)

        images = (
            Group(jagger_img, richards_img)
            .arrange(RIGHT, buff=0.2)
            .next_to(quote, buff=1)
        )

        Group(quote, images).move_to(ORIGIN + UP)

        main_text = (
            Tex(
                r"{{---Description of brute force SAT solving strategies \\ }}{{\text{from [Jagger, Richards, et al.; published in Out of Our Heads, 1965, available online]} }}",
            )
            .scale(0.7)
            .shift(3 * UP)
            .next_to(quote, DOWN, buff=1)
        )
        main_text[1].scale(0.7).align_to(main_text[0], LEFT)
        main_text.move_to([0, main_text.get_center()[1], 0])

        self.play(
            Write(quote),
            FadeIn(images),
            run_time=3,
        )

        self.play(Write(main_text))

        self.wait(3)


class NP5(Scene):
    def construct(self):
        texts = Group(
            *[
                Tex(text, color=text_color).scale(
                    1.5 if text == r"$\Rightarrow$" else 1.0
                )
                for text in [
                    r"We can verify \\ a potential solution. ",
                    r"$\Rightarrow$",
                    r"We can solve the problem. ",
                    r"We can compute $f$. ",
                    r"$\Rightarrow$",
                    r"We can compute $f^{-1}$. ",
                ]
            ]
        ).arrange_in_grid(rows=2, buff=1)
        texts[:3].shift(1.0 * UP)
        texts[3:].shift(0.5 * DOWN)

        eqs = [texts[1], texts[4]]
        smileys = [
            ImageMobject("img/sus.png").scale_to_fit_width(1).next_to(text, UP)
            for text in eqs
        ]
        ticks = [
            Text("✓", color=GREEN).scale_to_fit_height(1).next_to(text, UP)
            for text in eqs
        ]

        for i in range(2):
            self.play(Write(texts[3 * i]))
            self.wait(0.5)
            self.play(Write(texts[3 * i + 1]), FadeIn(smileys[i]))
            self.wait(0.5)
            self.play(Write(texts[3 * i + 2]))
            self.wait()

        self.play(
            *[FadeOut(s) for s in smileys],
        )
        self.play(
            *[FadeIn(t) for t in ticks],
        )
        self.wait()

        self.play(
            *[FadeOut(o) for o in self.mobjects],
        )
        self.wait()


class SHA(Scene):
    def construct(self):
        hash_tex = (
            Tex(r"Hash function", color=text_color)
            .scale(1.5)
            .to_edge(UP)
            .shift(config.frame_width / 4 * LEFT)
        )
        sha_img = (
            ImageMobject("img/sha.png")
            .scale_to_fit_height(config.frame_height * 0.9)
            .to_edge(RIGHT)
        )

        self.play(Write(hash_tex), FadeIn(sha_img))
        self.wait()

        arrow = Arrow(
            start=sha_img.get_top(), end=sha_img.get_bottom(), color=text_color, buff=1
        ).next_to(sha_img, LEFT, buff=1)
        arrow_tex = Tex(r"Easy", color=text_color).next_to(arrow, LEFT)

        self.play(Create(arrow), Write(arrow_tex))
        self.wait()

        self.play(
            Rotate(arrow, angle=PI, about_point=arrow.get_center()),
            Transform(arrow_tex, Tex(r"Hard", color=text_color).move_to(arrow_tex)),
        )
        self.wait()


class Outro(Scene):
    def construct(self):
        default()
        pnp_tex = Tex(r"P $\stackrel{?}{=}$ NP", color=text_color).scale(2).to_edge(UP)
        intuition1 = (
            Tex("Can we invert algorithms?", color=text_color)
            .scale(1)
            .next_to(pnp_tex, DOWN, buff=1)
        )
        intuition2 = (
            Tex("Can we solve problems if we can verify solutions?", color=text_color)
            .scale(1)
            .move_to(intuition1)
        )

        for t in [pnp_tex, intuition1]:
            self.play(Write(t))
            self.wait()

        self.play(
            Write(intuition2),
            FadeOut(intuition1),
        )
        self.wait()

        # thanks part
        patrons_thanks_text = "Our amazing Patrons:"
        patrons_text = [
            "Thomas Dubach",
            "Adam Zielinski",
            "Mika chu",
            "Hugo Madge León",
            "George Chahir",
            "Anh Dung Le",
            "Adam Dřínek",
            "Amit Nambiar",
            "Pepa Tkadlec",
            "sjbtrn",
            "George Mihaila",
            "Tomáš Sláma",
            "B J",
            "Jiří Nádvorník",
            "Matthew Aeschbacher",
        ]

        line = Line(10 * LEFT, 10 * RIGHT, color=text_color).next_to(
            intuition1, DOWN, buff=0.3
        )
        patrons_thanks_tex = (
            Tex(patrons_thanks_text, color=TEXT_COLOR)
            .scale(0.8)
            .next_to(intuition1, DOWN, buff=1)
        )
        patrons_tex = (
            VGroup(*[Tex(t, color=TEXT_COLOR).scale(0.75) for t in patrons_text])
            .arrange_in_grid(cell_alignment=LEFT + UP, buff=(0.5, 0.2))
            .next_to(patrons_thanks_tex, DOWN, buff=0.5)
        )

        # a cut here, a head-scene follows, then what's below
        self.remove(intuition2)
        self.add(intuition1)
        intuition1.shift(0.5 * UP)

        self.wait()
        self.play(
            AnimationGroup(
                Create(line),
                Write(patrons_thanks_tex),
                *[Write(t) for t in patrons_tex],
                lag_ratio=0.1,
            )
        )

        self.wait(5)
