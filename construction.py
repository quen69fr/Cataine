from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


class ConstructionKind(Enum):
    ROAD = 0
    COLONY = 1
    TOWN = 2


NUM_CONSTRUCTION_MAX = {  # TODO
    ConstructionKind.ROAD: 15,
    ConstructionKind.COLONY: 5,
    ConstructionKind.TOWN: 4
}


@dataclass
class Construction:
    kind: ConstructionKind
    player: Player
