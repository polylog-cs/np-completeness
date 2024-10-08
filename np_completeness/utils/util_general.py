import logging
import random
import sys
from typing import Any, TypeAlias

import manim
import numpy as np
from manim import *
from manim.typing import InternalPoint3D, Point2D, Point3D
from rich.logging import RichHandler

############### DEFAULT OPTIONS

random.seed(0)


def default():
    VMobject.set_default(color=GRAY)
    Polygon.set_default(color=RED)
    Text.set_default(color=GRAY)
    Tex.set_default(color=GRAY)
    VMobject.set_default(color=GRAY)
    # SurroundingRectangle.set_default(color = RED)
    # SurroundingRectangle.set_default(fill_color = config.background_color)
    # SurroundingRectangle.set_default(fill_opacity = 1)


############### GENERATING SOUNDS
# self.add_sound(file_name)


def random_click_file():
    return f"audio/click/click_{random.randint(0, 3)}.wav"


def random_pop_file():
    return f"audio/pop/pop_{random.randint(0, 6)}.wav"


def random_whoosh_file():
    return f"audio/whoosh/whoosh_{random.randint(0, 3)}.wav"


whoosh_gain = -8


def random_tick_file():
    return f"audio/tick/tick_{random.randint(0, 7)}.wav"


def random_whoops_file():
    return f"audio/whoops/whoops{random.randint(1, 1)}.mp3"


def random_rubik_file():
    return f"audio/cube/r{random.randint(1, 20)}.wav"


def random_typewriter_file():
    return f"audio/typewriter/t{random.randint(0, 9)}.wav"


def step_sound_file(randomize: bool = True):
    if randomize:
        return random_tick_file()
    else:
        return "audio/tick/tick_0.wav"


############### ANIMATIONS


def arrive_from(obj: Mobject, dir: InternalPoint3D, buff: float = 0.5):
    pos = obj.get_center()
    obj.align_to(Point().to_edge(dir, buff=0), -dir).shift(buff * dir)
    return obj.animate.move_to(pos)


############### SOLARIZED COLORS


# background tones (dark theme)

BASE03 = "#002b36"
BASE02 = "#073642"
BASE01 = "#586e75"

# content tones

BASE00 = "#657b83"  # dark gray
BASE0 = "#839496"  # light gray
BASE1 = "#93a1a1"

# background tones (light theme)

BASE2 = "#eee8d5"
BASE3 = "#fdf6e3"

# accent tones

YELLOW = "#d0b700"
YELLOW2 = "#b58900"  # The original Solarized yellow
ORANGE = "#c1670c"
ORANGE2 = "#cb4b16"  # The original Solarized orange - too close to red
RED = "#dc322f"
MAGENTA = "#d33682"
VIOLET = "#6c71c4"
BLUE = "#268bd2"
CYAN = "#2aa198"
CYAN2 = "#008080"
GREEN = "#859900"
HIGHLIGHT = YELLOW2

# Alias
GRAY = BASE00
GREY = BASE00

text_color = GRAY
TEXT_COLOR = GRAY
DALLE_ORANGE = r"#%02x%02x%02x" % (254, 145, 4)

# whenever more colors are needed
rainbow = [RED, MAGENTA, VIOLET, BLUE, CYAN, GREEN]
# [RED, ORANGE, GREEN, TEAL, BLUE, VIOLET, MAGENTA]
# [GREEN, TEAL, BLUE, VIOLET, MAGENTA, RED, ORANGE]

from manim import config

config.background_color = BASE2
BACKGROUND_COLOR_LIGHT = BASE2
BACKGROUND_COLOR_DARK = BASE02
BACKGROUND_COLOR = BACKGROUND_COLOR_LIGHT

config.max_files_cached = 1000


def disable_rich_logging():
    """Disable Manim's Rich-based logger because it's annoying.

    Manim uses the Python package Rich to format its logs.
    It tries to split lines nicely, but then it also splits file paths and then you can't
    command-click them to open them in the terminal.
    """
    # It seems that manim only has the rich handler, but let's remove it specifically
    # in case any file handlers are added under some circumstances.
    for handler in manim.logger.handlers:
        if isinstance(handler, RichHandler):
            manim.logger.handlers.remove(handler)

    ANSI_DARK_GRAY = "\033[1;30m"
    ANSI_END = "\033[0m"

    # Add a new handler with a given format. Note that the removal above is still needed
    # because otherwise we get two copies of the same log messages.
    logging.basicConfig(
        format=f"{ANSI_DARK_GRAY}%(asctime)s %(levelname)s{ANSI_END} %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


disable_rich_logging()

#### Video-specific


GATE_WIDTH = 0.5
GATE_HEIGHT = 0.3
SIGNAL_SPEED = 2.5  # units per second

WIRE_COLOR_NONE = BASE00
WIRE_COLOR_TRUE = YELLOW
WIRE_COLOR_FALSE = BASE02
WIRE_WIDTH = 5
WIRE_TIGHT_SPACING = 0.1

GATE_TEXT_RATIO = 0.4
GATE_X_SPACING = 1.2
GATE_Y_SPACING = 1
DEFAULT_GATE_LENGTH = 0.5


def get_wire_color(value: bool | None) -> str:
    match value:
        case True:
            return WIRE_COLOR_TRUE
        case False:
            return WIRE_COLOR_FALSE
        case None:
            return WIRE_COLOR_NONE


AnyPoint: TypeAlias = Point3D | Point2D


def normalize_position(position: AnyPoint) -> InternalPoint3D:
    if isinstance(position, tuple):
        if len(position) == 2:
            position = np.array([*position, 0])
        elif len(position) == 3:
            position = np.array(position)
        else:
            raise ValueError(f"Invalid position: {position}")
    else:
        if position.shape == (2,):
            position = np.array([*position, 0])
        elif position.shape == (3,):
            pass
        else:
            raise ValueError(f"Invalid position: {position}")

    return position.astype(np.float64)


def animate(mobject: Mobject) -> Any:
    """A hack to work around the fact that Manim's typing for .animate sucks."""
    return mobject.animate


def center_of(mobject: Mobject) -> InternalPoint3D:
    """Another hack to work around Manim's typing.

    It thinks get_center() might return a tuple of floats, but that never happens.
    """
    center = mobject.get_center()
    assert isinstance(center, np.ndarray)
    return center


def submobjects_of(mobject: VMobject) -> list[VMobject]:
    return mobject.submobjects


eq_str = r"{{$\,=\,$}}"
not_str = r"{{NOT\;}}"
and_str = r"{{\;AND\;}}"
or_str = r"{{\;OR\;}}"
left_str = r"{{$($}}"
right_str = r"{{$)$}}"
x1_str = r"{{$a$}}"
x2_str = r"{{$b$}}"
x3_str = r"{{$c$}}"
x4_str = r"{{$d$}}"
x5_str = r"{{$e$}}"
x6_str = r"{{$f$}}"
true_str = r"{{TRUE}}"
false_str = r"{{FALSE}}"
one_str = r"{{1}}"
zero_str = r"{{0}}"


def coltex(s: str, color: str = GRAY, **kwargs: Any) -> Tex:
    d = {
        not_str: RED,
        or_str: BLUE,
        and_str: ORANGE,
        true_str: WIRE_COLOR_TRUE,
        false_str: WIRE_COLOR_FALSE,
        one_str: WIRE_COLOR_TRUE,
        zero_str: WIRE_COLOR_FALSE,
    }
    tex = Tex(s, **kwargs)
    for subtex in tex:
        new_color = d.get("{{" + subtex.get_tex_string() + "}}", color)
        subtex.set_color(new_color)
    return tex
