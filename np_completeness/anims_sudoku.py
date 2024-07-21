import numpy as np
from manim import *


class Sudoku(VGroup):
    def __init__(self, unsolved, solution, cell_size=0.5):
        super().__init__()
        self.unsolved = np.array(unsolved)
        self.solution = np.array(solution)
        self.current_state = self.unsolved.copy()
        self.cell_size = cell_size
        self.grid = self.create_grid()
        self.add(self.grid)
        self.reveal_one_hot_encoding()
        self.is_3d_cube = False

    def create_grid(self):
        grid = VGroup()
        for i in range(9):
            for j in range(9):
                cell = Square(side_length=self.cell_size)
                if self.unsolved[i][j] != 0:
                    number = Text(str(self.unsolved[i][j]), font_size=24)
                    number.move_to(cell.get_center())
                    cell.add(number)
                grid.add(cell)
        grid.arrange_in_grid(rows=9, cols=9, buff=0)
        grid.move_to(ORIGIN)

        thick_lines = VGroup()
        for i in range(4):
            thick_lines.add(
                Line(
                    grid.get_corner(UL) + RIGHT * i * 3 * self.cell_size,
                    grid.get_corner(DL) + RIGHT * i * 3 * self.cell_size,
                    stroke_width=3,
                )
            )
            thick_lines.add(
                Line(
                    grid.get_corner(UL) + DOWN * i * 3 * self.cell_size,
                    grid.get_corner(UR) + DOWN * i * 3 * self.cell_size,
                    stroke_width=3,
                )
            )

        return VGroup(grid, thick_lines)

    def reveal_grid(self):
        return Create(self.grid)

    def reveal_one_hot_encoding(self):
        self.is_3d_cube = True
        self.cube = VGroup()
        for i in range(9):
            plane = VGroup()
            for j in range(9):
                row = VGroup()
                for k in range(9):
                    tex = MathTex(f"x_{{{j+1},{k+1}}}^{{{i+1}}}", font_size=24).move_to(
                        self.grid[0][j * 9 + k].get_center() + 0.5 * i * IN
                    )
                    if self.current_state[j][k] == i + 1:
                        tex.set_color(YELLOW)
                    row.add(tex)
                # row.arrange(RIGHT, buff=0.2)
                plane.add(row)
            # plane.arrange(DOWN, buff=0.2)
            self.cube.add(plane)
        # self.cube.arrange(OUT, buff=0.5)
        self.cube.move_to(self.grid.get_center())

        return FadeOut(self.grid), Create(self.cube)

    def reveal_cell_variables(self, row, col, rg=range(9)):
        if not self.is_3d_cube:
            raise Exception("One-hot encoding must be revealed first.")
        return AnimationGroup(
            *[self.cube[i][row][col].animate.set_color(BLUE) for i in rg]
        )

    def fill_in(self):
        new_numbers = []
        for i in range(9):
            for j in range(9):
                if self.unsolved[i][j] == 0:
                    new_number = Text(str(self.solution[i][j]), font_size=24)
                    new_number.move_to(self.grid[0][i * 9 + j])
                    new_numbers.append(new_number)
                    self.current_state[i][j] = self.solution[i][j]
        self.grid[0].add(*new_numbers)
        return AnimationGroup(*[Write(num) for num in new_numbers])

    def unfill(self):
        removals = []
        for i in range(9):
            for j in range(9):
                if self.unsolved[i][j] == 0:
                    cell = self.grid[0][i * 9 + j]
                    if len(cell.submobjects) > 0:
                        removals.append(FadeOut(cell.submobjects[0]))
                        cell.remove(cell.submobjects[0])
                    self.current_state[i][j] = 0
        return AnimationGroup(*removals)

    def highlight_row(self, row):
        if self.is_3d_cube:
            highlights = [
                self.cube[i][row][j].animate.set_color(RED)
                for i in range(9)
                for j in range(9)
            ]
            unhighlights = [
                self.cube[i][row][j].animate.set_color(WHITE)
                for i in range(9)
                for j in range(9)
                if self.current_state[row][j] != i + 1
            ]
            return AnimationGroup(*highlights), AnimationGroup(*unhighlights)
        else:
            highlight = SurroundingRectangle(
                VGroup(*self.grid[0][row * 9 : (row + 1) * 9]), color=RED
            )
            return Create(highlight), FadeOut(highlight)

    def highlight_column(self, col):
        if self.is_3d_cube:
            highlights = [
                self.cube[i][j][col].animate.set_color(GREEN)
                for i in range(9)
                for j in range(9)
            ]
            unhighlights = [
                self.cube[i][j][col].animate.set_color(WHITE)
                for i in range(9)
                for j in range(9)
                if self.current_state[j][col] != i + 1
            ]
            return AnimationGroup(*highlights), AnimationGroup(*unhighlights)
        else:
            highlight = SurroundingRectangle(
                VGroup(*[self.grid[0][i * 9 + col] for i in range(9)]), color=GREEN
            )
            return Create(highlight), FadeOut(highlight)

    def highlight_cell(self, row, col):
        if self.is_3d_cube:
            highlights = [
                self.cube[i][row][col].animate.set_color(BLUE) for i in range(9)
            ]
            unhighlights = [
                self.cube[i][row][col].animate.set_color(WHITE)
                for i in range(9)
                if i + 1 != self.current_state[row][col]
            ]
            return AnimationGroup(*highlights), AnimationGroup(*unhighlights)
        else:
            highlight = SurroundingRectangle(self.grid[0][row * 9 + col], color=BLUE)
            return Create(highlight), FadeOut(highlight)


class SudokuVisualizer(ThreeDScene):
    def construct(self):
        unsolved = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

        solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

        sudoku = Sudoku(unsolved, solution)

        print(sudoku.grid[0][4 * 9 + 8].get_center())
        print(sudoku.cube[0][4][8].get_center())

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        self.play(sudoku.reveal_grid())
        self.wait()

        # self.play(Rotate(sudoku, angle=-0.3 * PI, axis=UP, run_time=5))
        self.move_camera(phi=60 * DEGREES, theta=(-90 + 45) * DEGREES, run_time=3)
        self.wait()

        sudoku.is_3d_cube = True

        self.play(sudoku.reveal_cell_variables(4, 8))
        self.wait()


if __name__ == "__main__":
    scene = SudokuVisualizer()
    scene.render()
