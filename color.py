from __future__ import annotations
from enum import Enum


class Color(Enum):
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    ORANGE = (255, 127, 0)
    RED = (255, 0, 0)


COLORS_ORDER = [Color.BLUE, Color.ORANGE, Color.WHITE, Color.RED]
