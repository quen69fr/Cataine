from __future__ import annotations

import random
from abc import abstractmethod
from typing import TYPE_CHECKING, Generator

from actions import Action, ActionBuildColony, ActionBuildRoad
from board import Board
from tile import Tile
from tile_intersection import TileIntersection

if TYPE_CHECKING:
    from player import Player

from probability import get_expectation_of_intersection
from resource import Resource

class Strategy:

    @abstractmethod
    def play(self, board: Board, player: Player, all_actions: list[list[Action]]) -> list[Action]:
        pass


class StrategyChooseRandom(Strategy):

    def play(self, board: Board, player: Player, all_actions: list[list[Action]]) -> list[Action]:
        result = random.choice(all_actions)
        return result

class StrategyExplorer(Strategy):

    current_objective: list[Action] | None

    def __init__(self):
        self.current_objective = None

    def play(self, board: Board, player: Player, all_actions: list[list[Action]]) -> list[Action]:
        if self.current_objective is None:
            actions = self._select_objective(board, player)
            self.current_objective = actions
            print(actions)

        self._do_objective()

    def _select_objective(self, board: Board, player: Player):
        assert self.current_objective is None

        # find where my roads are
        starts = list(find_all_intersection_belonging_to_player(board, player))
        distances: dict[TileIntersection, int] = {}
        for start in starts:
            distances[start] = 0

        for path in find_all_path_belonging_to_player(board, player):
            if path.intersections[0] not in starts:
                starts.append(path.intersections[0])
            if path.intersections[1] not in starts:
                starts.append(path.intersections[1])


        q = starts
        while q:
            inte = q.pop(0)
            d = distances[inte] + 1
            for path in inte.neighbour_paths:
                if path.road_player == player:
                    d = 0
                for neigh in path.intersections:
                    if not neigh in distances:
                        distances[neigh] = d
                        q.append(neigh)


        # rank all intersections
        # select the best one and do it

        rank: dict[TileIntersection, float] = {}
        m = None
        for inte, d in distances.items():
            if not inte.can_build():
                print("can't build here")
                continue

            rank[inte] = neighbour_tiles_expectation(inte) - d / 6
            if m is None or rank[inte] > rank[m]:
                m = inte

        if m is None:
            return None

        actions: list[Action] = [ActionBuildColony(m, player)]
        curr = m
        print(distances[m])
        for i in range(distances[m]):
            for path, inte in curr.neighbour_paths_intersection():
                if path.road_player is None and distances[inte] == distances[curr] - 1:
                    actions.insert(0, ActionBuildRoad(path, player))
                    curr = inte
                    break

        return actions

    def _do_objective(self):
        raise NotImplemented

def find_all_intersection_belonging_to_player(board: Board, player: Player) -> Generator[TileIntersection]:
    for inte in board.intersections:
        if inte.content is not None and inte.content.player == player:
            yield inte

def find_all_path_belonging_to_player(board: Board, player: Player) -> Generator[TilePath]:
    for path in board.paths:
        if path.road_player == player:
            yield path

def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(
        t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)

