from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from resource import Resource
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


class ConstructionKind(Enum):
    ROAD = 0
    COLONY = 1
    TOWN = 2


@dataclass
class Construction:
    kind: ConstructionKind
    player: Player


COST_CONSTRUCTIONS = {
    ConstructionKind.ROAD: [Resource.WOOD, Resource.CLAY],
    ConstructionKind.COLONY: [Resource.WOOD, Resource.CLAY, Resource.WOOD, Resource.HAY],
    ConstructionKind.TOWN: [Resource.HAY] * 2 + [Resource.ROCK] * 3
}

COST_DEV_CARD = [Resource.WOOD, Resource.HAY, Resource.ROCK]
