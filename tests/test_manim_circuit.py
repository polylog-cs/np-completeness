from typing import cast

import numpy as np
from manim import RIGHT, Animation, Scene

from np_completeness.utils.manim_circuit import ManimCircuit
from tests.test_circuit import make_circuit_fixture


def test_animation_after_shift():
    circuit = make_circuit_fixture()
    manim_circuit = ManimCircuit(circuit, scale=2)

    scene = Scene()

    scene.add(manim_circuit)
    scene.play(cast(Animation, manim_circuit.animate.shift(RIGHT).scale(0.8)))

    positions_1 = [m.get_center() for m in manim_circuit.submobjects]
    scene.wait()
    scene.play(manim_circuit.animate_evaluation(speed=5))
    scene.wait()
    positions_2 = [m.get_center() for m in manim_circuit.submobjects]

    # There was a bug where .animate_evaluation() would move mobjects to the positions
    # they were at before the shift. This test checks that this doesn't happen any more.
    for p1, p2 in zip(positions_1, positions_2):
        np.testing.assert_almost_equal(p1, p2)
