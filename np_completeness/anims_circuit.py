from manim import *

from np_completeness.utils.manim_circuit import ManimCircuit
from np_completeness.utils.specific_circuits import (
    make_example_circuit,
    make_multiplication_circuit,
)

# Imported for the side effect of changing the default colors
from np_completeness.utils.util_general import BASE00, MAGENTA, disable_rich_logging


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


def lagged_create(objects: list[VMobject], lag_ratio: float = 0.1) -> AnimationGroup:
    return LaggedStart(*[Create(obj) for obj in objects], lag_ratio=lag_ratio)


class MultiplicationByHand(Scene):
    def construct(self):
        disable_rich_logging()

        grid = [
            "  68",
            "× 18",
            " 544",
            " 680",
            "1224",
        ]
        group, _, _ = make_multiplication_by_hand(grid)
        group.scale(2).center()

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
        group.scale(2).center().shift(LEFT * 2)

        self.play(lagged_create(numbers[0] + numbers[1]))
        self.wait(1)
        base10_rows = [
            Tex("=3", color=MAGENTA),
            Tex("=5", color=MAGENTA),
            VGroup(),
            VGroup(),
            VGroup(),
            Tex("=15", color=MAGENTA),
        ]

        for i, row in enumerate(base10_rows):
            row.scale(2).next_to(
                numbers[i][-1], direction=RIGHT, buff=1, aligned_edge=DOWN
            )

        # this is what it is in base10
        self.play(lagged_create([base10_rows[0], base10_rows[1]]))
        self.wait(1)
        # intermediate results
        self.play(lagged_create([lines[0], *numbers[2], *numbers[3], *numbers[4]]))
        self.wait(1)
        # final result, explanation in base10
        self.play(lagged_create([lines[1], *numbers[5], base10_rows[5]]))
        self.wait(1)


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
