from __future__ import annotations
from enum import Enum

from resource import Resource


class Construction(Enum):
    ROAD = 0
    COLONY = 1
    TOWN = 2


COST_CONSTRUCTIONS = {
    Construction.ROAD: [Resource.WOOD, Resource.CLAY],
    Construction.COLONY: [Resource.WOOD, Resource.CLAY, Resource.WOOD, Resource.HAY],
    Construction.TOWN: [Resource.HAY] * 2 + [Resource.ROCK] * 3
}

COST_DEV_CARD = [Resource.WOOD, Resource.HAY, Resource.ROCK]
