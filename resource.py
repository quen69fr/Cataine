from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


class Resource(Enum):
    DESERT = 0
    CLAY = 1
    WOOL = 2
    HAY = 3
    ROCK = 4
    WOOD = 5
    P_3_FOR_1 = 6


ORDER_RESOURCES = [Resource.WOOD, Resource.CLAY, Resource.WOOL, Resource.HAY, Resource.ROCK]


@dataclass
class Port:
    resource: Resource
    direction: int


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

BOARD_PORT_RESOURCES = [
    Resource.P_3_FOR_1,
    Resource.WOOL,
    Resource.ROCK,
    Resource.P_3_FOR_1,
    Resource.P_3_FOR_1,
    Resource.HAY,
    Resource.CLAY,
    Resource.P_3_FOR_1,
    Resource.WOOD
]
BOARD_PORT_INDEXES_PATHS = [5, 6, 19, 27, 46, 52, 60, 64, 67]
BOARD_PORT_DIRECTION = [120, 60, -180, 60, 0, -180, -60, -120, -60]  # In degrees
