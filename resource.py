from __future__ import annotations
from enum import Enum


class Resource(Enum):
    DESERT = 0
    CLAY = 1
    WOOL = 2
    HAY = 3
    ROCK = 4
    WOOD = 5


BOARD_LAYOUT_RESOURCES = [
    Resource.WOOD,
    Resource.WOOL,
    Resource.WOOL,
    Resource.HAY,
    Resource.ROCK,
    Resource.HAY,
    Resource.WOOD,
    Resource.WOOD,
    Resource.CLAY,
    Resource.DESERT,
    Resource.ROCK,
    Resource.HAY,
    Resource.HAY,
    Resource.ROCK,
    Resource.WOOD,
    Resource.WOOL,
    Resource.CLAY,
    Resource.WOOL,
    Resource.CLAY
]

BOARD_LAYOUT_DICE_NUMBERS = [6, 3, 8, 2, 4, 5, 10, 5, 9, 0, 6, 9, 10, 11, 3, 12, 8, 4, 11]
