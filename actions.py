from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from yaml import add_path_resolver

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

    def available(self):
        # path is occupied
        if self.path.content is not None:
            return False

        # check if there is one of our colony/town around it
        has_own_construction = lambda intersection: intersection.content is not None \
            and intersection.content.player == self.player

        if has_own_construction(self.path.intersections[0]) or \
           has_own_construction(self.path.intersections[1]):
           return True
        
        # check if there is one of our road around it
        adjacent_paths = self.path.intersections[0].neighbour_paths + self.path.intersections[1].neighbour_paths
        for p in adjacent_paths:
            if p.road_player == self.player:
                return True

        return False
