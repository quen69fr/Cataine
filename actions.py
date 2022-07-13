from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from tile_path import TilePath


class Action:
    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def available(self, player: Player):
        pass


@dataclass
class ActionBuildRoad(Action):
    path: TilePath
    player: Player

    def apply(self):
        if self.path.road_player is not None:
            raise ValueError("building road on a tile path that already has a tile path")
        self.path.road_player = self.player

    def undo(self):
        assert self.path.road_player == self.path
        self.path.road_player = None

    def available(self, player: Player):
        assert player == self.player
        # check if there is a road around it
        # check if there is a colony around it
        # if
