from __future__ import annotations

from collections import namedtuple
from enum import Enum
from resource import Resource


class ConstructionKind(Enum):
    ROAD = 0
    COLONY = 1
    TOWN = 2

Construction = namedtuple('Construction', ['kind', 'player'])

COST_CONSTRUCTIONS = {
    ConstructionKind.ROAD: [Resource.WOOD, Resource.CLAY],
    ConstructionKind.COLONY: [Resource.WOOD, Resource.CLAY, Resource.WOOD, Resource.HAY],
    ConstructionKind.TOWN: [Resource.HAY] * 2 + [Resource.ROCK] * 3
}

COST_DEV_CARD = [Resource.WOOD, Resource.HAY, Resource.ROCK]
