import logging
import random
import sys
from typing import TypeAlias

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
GATE_HORIZONTAL_SPACING = 1.2
GATE_VERTICAL_SPACING = 1
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


CNF_NUM_VARS = 82
CNF_CONSTRAINTS = [[-1, -5, 9], [1, -9], [5, -9], [-1, -6, 10], [1, -10], [6, -10], [-1, -7, 11], [1, -11], [7, -11], [-1, -8, 12], [1, -12], [8, -12], [-2, -5, 13], [2, -13], [5, -13], [-2, -6, 14], [2, -14], [6, -14], [-2, -7, 15], [2, -15], [7, -15], [-2, -8, 16], [2, -16], [8, -16], [-3, -5, 17], [3, -17], [5, -17], [-3, -6, 18], [3, -18], [6, -18], [-3, -7, 19], [3, -19], [7, -19], [-3, -8, 20], [3, -20], [8, -20], [-4, -5, 21], [4, -21], [5, -21], [-4, -6, 22], [4, -22], [6, -22], [-4, -7, 23], [4, -23], [7, -23], [-4, -8, 24], [4, -24], [8, -24], [9, 82, 82, -25], [9, 82, -82, 25], [9, -82, 82, 25], [-9, 82, 82, 25], [9, -82, -82, -25], [-9, 82, -82, -25], [-9, -82, 82, -25], [-9, -82, -82, 25], [-9, -82, 49], [-9, -82, 49], [-82, -82, 49], [9, 82, -49], [9, 82, -49], [82, 82, -49], [10, 13, 49, -26], [10, 13, -49, 26], [10, -13, 49, 26], [-10, 13, 49, 26], [10, -13, -49, -26], [-10, 13, -49, -26], [-10, -13, 49, -26], [-10, -13, -49, 26], [-10, -13, 50], [-10, -49, 50], [-13, -49, 50], [10, 13, -50], [10, 49, -50], [13, 49, -50], [11, 14, 50, -27], [11, 14, -50, 27], [11, -14, 50, 27], [-11, 14, 50, 27], [11, -14, -50, -27], [-11, 14, -50, -27], [-11, -14, 50, -27], [-11, -14, -50, 27], [-11, -14, 51], [-11, -50, 51], [-14, -50, 51], [11, 14, -51], [11, 50, -51], [14, 50, -51], [12, 15, 51, -28], [12, 15, -51, 28], [12, -15, 51, 28], [-12, 15, 51, 28], [12, -15, -51, -28], [-12, 15, -51, -28], [-12, -15, 51, -28], [-12, -15, -51, 28], [-12, -15, 52], [-12, -51, 52], [-15, -51, 52], [12, 15, -52], [12, 51, -52], [15, 51, -52], [82, 16, 52, -29], [82, 16, -52, 29], [82, -16, 52, 29], [-82, 16, 52, 29], [82, -16, -52, -29], [-82, 16, -52, -29], [-82, -16, 52, -29], [-82, -16, -52, 29], [-82, -16, 53], [-82, -52, 53], [-16, -52, 53], [82, 16, -53], [82, 52, -53], [16, 52, -53], [82, 82, 53, -30], [82, 82, -53, 30], [82, -82, 53, 30], [-82, 82, 53, 30], [82, -82, -53, -30], [-82, 82, -53, -30], [-82, -82, 53, -30], [-82, -82, -53, 30], [-82, -82, 54], [-82, -53, 54], [-82, -53, 54], [82, 82, -54], [82, 53, -54], [82, 53, -54], [82, 82, 54, -31], [82, 82, -54, 31], [82, -82, 54, 31], [-82, 82, 54, 31], [82, -82, -54, -31], [-82, 82, -54, -31], [-82, -82, 54, -31], [-82, -82, -54, 31], [-82, -82, 55], [-82, -54, 55], [-82, -54, 55], [82, 82, -55], [82, 54, -55], [82, 54, -55], [82, 82, 55, -32], [82, 82, -55, 32], [82, -82, 55, 32], [-82, 82, 55, 32], [82, -82, -55, -32], [-82, 82, -55, -32], [-82, -82, 55, -32], [-82, -82, -55, 32], [-82, -82, 56], [-82, -55, 56], [-82, -55, 56], [82, 82, -56], [82, 55, -56], [82, 55, -56], [25, 82, 82, -33], [25, 82, -82, 33], [25, -82, 82, 33], [-25, 82, 82, 33], [25, -82, -82, -33], [-25, 82, -82, -33], [-25, -82, 82, -33], [-25, -82, -82, 33], [-25, -82, 57], [-25, -82, 57], [-82, -82, 57], [25, 82, -57], [25, 82, -57], [82, 82, -57], [26, 82, 57, -34], [26, 82, -57, 34], [26, -82, 57, 34], [-26, 82, 57, 34], [26, -82, -57, -34], [-26, 82, -57, -34], [-26, -82, 57, -34], [-26, -82, -57, 34], [-26, -82, 58], [-26, -57, 58], [-82, -57, 58], [26, 82, -58], [26, 57, -58], [82, 57, -58], [27, 17, 58, -35], [27, 17, -58, 35], [27, -17, 58, 35], [-27, 17, 58, 35], [27, -17, -58, -35], [-27, 17, -58, -35], [-27, -17, 58, -35], [-27, -17, -58, 35], [-27, -17, 59], [-27, -58, 59], [-17, -58, 59], [27, 17, -59], [27, 58, -59], [17, 58, -59], [28, 18, 59, -36], [28, 18, -59, 36], [28, -18, 59, 36], [-28, 18, 59, 36], [28, -18, -59, -36], [-28, 18, -59, -36], [-28, -18, 59, -36], [-28, -18, -59, 36], [-28, -18, 60], [-28, -59, 60], [-18, -59, 60], [28, 18, -60], [28, 59, -60], [18, 59, -60], [29, 19, 60, -37], [29, 19, -60, 37], [29, -19, 60, 37], [-29, 19, 60, 37], [29, -19, -60, -37], [-29, 19, -60, -37], [-29, -19, 60, -37], [-29, -19, -60, 37], [-29, -19, 61], [-29, -60, 61], [-19, -60, 61], [29, 19, -61], [29, 60, -61], [19, 60, -61], [30, 20, 61, -38], [30, 20, -61, 38], [30, -20, 61, 38], [-30, 20, 61, 38], [30, -20, -61, -38], [-30, 20, -61, -38], [-30, -20, 61, -38], [-30, -20, -61, 38], [-30, -20, 62], [-30, -61, 62], [-20, -61, 62], [30, 20, -62], [30, 61, -62], [20, 61, -62], [31, 82, 62, -39], [31, 82, -62, 39], [31, -82, 62, 39], [-31, 82, 62, 39], [31, -82, -62, -39], [-31, 82, -62, -39], [-31, -82, 62, -39], [-31, -82, -62, 39], [-31, -82, 63], [-31, -62, 63], [-82, -62, 63], [31, 82, -63], [31, 62, -63], [82, 62, -63], [32, 82, 63, -40], [32, 82, -63, 40], [32, -82, 63, 40], [-32, 82, 63, 40], [32, -82, -63, -40], [-32, 82, -63, -40], [-32, -82, 63, -40], [-32, -82, -63, 40], [-32, -82, 64], [-32, -63, 64], [-82, -63, 64], [32, 82, -64], [32, 63, -64], [82, 63, -64], [33, 82, 82, -41], [33, 82, -82, 41], [33, -82, 82, 41], [-33, 82, 82, 41], [33, -82, -82, -41], [-33, 82, -82, -41], [-33, -82, 82, -41], [-33, -82, -82, 41], [-33, -82, 65], [-33, -82, 65], [-82, -82, 65], [33, 82, -65], [33, 82, -65], [82, 82, -65], [34, 82, 65, -42], [34, 82, -65, 42], [34, -82, 65, 42], [-34, 82, 65, 42], [34, -82, -65, -42], [-34, 82, -65, -42], [-34, -82, 65, -42], [-34, -82, -65, 42], [-34, -82, 66], [-34, -65, 66], [-82, -65, 66], [34, 82, -66], [34, 65, -66], [82, 65, -66], [35, 82, 66, -43], [35, 82, -66, 43], [35, -82, 66, 43], [-35, 82, 66, 43], [35, -82, -66, -43], [-35, 82, -66, -43], [-35, -82, 66, -43], [-35, -82, -66, 43], [-35, -82, 67], [-35, -66, 67], [-82, -66, 67], [35, 82, -67], [35, 66, -67], [82, 66, -67], [36, 21, 67, -44], [36, 21, -67, 44], [36, -21, 67, 44], [-36, 21, 67, 44], [36, -21, -67, -44], [-36, 21, -67, -44], [-36, -21, 67, -44], [-36, -21, -67, 44], [-36, -21, 68], [-36, -67, 68], [-21, -67, 68], [36, 21, -68], [36, 67, -68], [21, 67, -68], [37, 22, 68, -45], [37, 22, -68, 45], [37, -22, 68, 45], [-37, 22, 68, 45], [37, -22, -68, -45], [-37, 22, -68, -45], [-37, -22, 68, -45], [-37, -22, -68, 45], [-37, -22, 69], [-37, -68, 69], [-22, -68, 69], [37, 22, -69], [37, 68, -69], [22, 68, -69], [38, 23, 69, -46], [38, 23, -69, 46], [38, -23, 69, 46], [-38, 23, 69, 46], [38, -23, -69, -46], [-38, 23, -69, -46], [-38, -23, 69, -46], [-38, -23, -69, 46], [-38, -23, 70], [-38, -69, 70], [-23, -69, 70], [38, 23, -70], [38, 69, -70], [23, 69, -70], [39, 24, 70, -47], [39, 24, -70, 47], [39, -24, 70, 47], [-39, 24, 70, 47], [39, -24, -70, -47], [-39, 24, -70, -47], [-39, -24, 70, -47], [-39, -24, -70, 47], [-39, -24, 71], [-39, -70, 71], [-24, -70, 71], [39, 24, -71], [39, 70, -71], [24, 70, -71], [40, 82, 71, -48], [40, 82, -71, 48], [40, -82, 71, 48], [-40, 82, 71, 48], [40, -82, -71, -48], [-40, 82, -71, -48], [-40, -82, 71, -48], [-40, -82, -71, 48], [-40, -82, 72], [-40, -71, 72], [-82, -71, 72], [40, 82, -72], [40, 71, -72], [82, 71, -72], [-41, 73], [41, -73], [-42, 74], [42, -74], [-43, 75], [43, -75], [-44, 76], [44, -76], [-45, 77], [45, -77], [-46, 78], [46, -78], [-47, 79], [47, -79], [-48, 80], [48, -80], [2, 3, 4, -1], [6, 7, 8, -5], [81], [-82], ]
