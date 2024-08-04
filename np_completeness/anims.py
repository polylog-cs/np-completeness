# manim -pql --disable_caching --fps 15 -r 290,180 anims.py Polylogo
from utils.util_general import *


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
        np_rect = Rectangle(width=7, height=5, color = text_color).to_edge(LEFT, buff = 2)
        np_label = Tex(r"\raggedright NP = verification \\ in polynomial time").next_to(np_rect, RIGHT).align_to(np_rect, UP)
        
        problems = ["SATISFIABILITY", "COLORING", "FACTORING", "MULTIPLYING"]
        problem_texs = [Tex(problem) for problem in problems]
        problem_rects = Group(*[Group(tex, SurroundingRectangle(tex, color = text_color)) for tex in problem_texs])
        print(len(problem_rects))
        problem_rects[0].next_to(np_rect, UP, buff=0.5)
        problem_rects[1:].arrange(DOWN).move_to(np_rect.get_center()).shift(0.5*DOWN)
        problem_rects[1].shift(1.5*LEFT)
        problem_rects[2].shift(0.2*RIGHT)
        problem_rects[3].shift(1*RIGHT)

        self.play(Create(np_rect), Write(np_label))
        for rect in problem_rects[1:]:
            self.play(Write(rect[0]), Create(rect[1]))
        self.wait()

        self.play(Write(problem_rects[0][0]), Create(problem_rects[0][1]))
        self.wait()
        
        shifts = [1*LEFT, 0*LEFT, 1*RIGHT]
        # Our trick with converting algorithms to SAT problems works in polynomial time.
        arrows = []
        for i in range(3):
            start = problem_rects[i+1].get_top()
            end = problem_rects[0].get_bottom() + shifts[i]
            arrow = Arrow(start=start, end=end, buff=0.1)  # Added a small buffer
            arrows.append(arrow)
        arrows = VGroup(*arrows)


        self.play(*[GrowArrow(arrow) for arrow in arrows])
        self.wait()
        
        # This means that a SAT solver that runs in polynomial time would imply polynomial-time solution for *any* problem in NP.
        poly_labels = VGroup(*[Tex("polynomial", color = BLUE, font_size=30).next_to(rect, UP).align_to(rect, RIGHT) for rect in problem_rects])
        self.play(Write(poly_labels[0]))
        self.play(*[ReplacementTransform(poly_labels[0].copy(), label) for label in poly_labels[1:]])
        self.wait()
        
        self.play(
            *[FadeOut(obj) for obj in poly_labels],
        )
        self.wait()

        # But here's a fun fact: The satisfiability problem is *itself *in the class NP.
        problem_rects[0].generate_target()
        problem_rects[0].target.align_to(np_rect, UP).shift(0.5*DOWN)

        self.play(
            MoveToTarget(problem_rects[0]),
            *[ar.animate.put_start_and_end_on(ar.get_start(), problem_rects[0].target.get_bottom() + shifts[i]) for i, ar in enumerate(arrows)],
            )
        self.wait()



class NP2(Scene):
    def construct(self):
        default()

        npc_tex = Tex(r"{{\raggedright A problem is NP-complete if: \\}}{{ 1. It is in NP.  \\}}{{ 2. Every problem in NP is reducible to it \\ \;\;\;\; in polynomial time. }}")

        for i in range(3):
            self.play(Write(npc_tex[i]))
            self.wait(0.5)
        self.wait()
        self.play(
            FadeOut(npc_tex),
        )
        self.wait()
        
        thm_tex = Tex(r"SATISFIABILITY is NP-complete. ").scale(1.5).to_edge(UP, buff = 1)
        self.play(Write(thm_tex))
        images = Group(*[
            Group(
                ImageMobject(path).scale_to_fit_height(3.5),
                Tex(name)
            ).arrange(DOWN)
            for path, name in [
                ("img/cook.webp", "Stephen Cook"),
                ("img/levin.jpeg", "Leonid Levin"),
            ]
        ]).arrange(RIGHT, buff = 1).shift(0.5*DOWN + 1.5*LEFT)

        self.play(
            FadeIn(images[0])
        )
        self.play(
            FadeIn(images[1])
        )
        self.wait()

        thumb = ImageMobject("img/thumbnail2.png").scale_to_fit_width(4).to_edge(RIGHT)
        rec = SurroundingRectangle(thumb, color = text_color)
        thumb = Group(thumb, rec)

        self.play(FadeIn(thumb))
        self.wait()
        


class NP3(Scene):
    def construct(self):
        default()

