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
    def play(self, board: Board, player: Player):
        pass


# class StrategyChooseRandom(Strategy):

#     def play(self, board: Board, player: Player, all_actions: list[list[Action]]) -> list[Action]:
#         result = random.choice(all_actions)
#         return result

class ObjectiveBuildColony:

    def __init__(self, board: Board, player: Player) -> None:
        self.board = board
        self.player = player

        self.actions = []
        self.cost = None
        self.gain = None

    def do(self):
        # find where my roads are
        starts = list(self.player.find_all_intersection_belonging_to_player(self.board))
        distances: dict[TileIntersection, int] = {}
        for start in starts:
            distances[start] = 0

        for path in self.player.find_all_path_belonging_to_player(self.board):
            if path.intersections[0] not in starts:
                starts.append(path.intersections[0])
            if path.intersections[1] not in starts:
                starts.append(path.intersections[1])


        q = starts
        while q:
            inte = q.pop(0)
            d = distances[inte] + 1
            for path in inte.neighbour_paths:
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
                continue

            rank[inte] = inte.neighbour_tiles_expectation() - d / 6
            if m is None or rank[inte] > rank[m]:
                m = inte

        if m is None:
            return []

        actions: list[Action] = [ActionBuildColony(m, self.player)]
        curr = m
        cost = []
        for i in range(distances[m]):
            for path, inte in curr.neighbour_paths_intersection():
                if path.road_player is None and distances[inte] == distances[curr] - 1:
                    actions.insert(0, ActionBuildRoad(path, self.player))
                    curr = inte
                    break

        # build list of required cards - current hand
        # max of the inverse probabilities for each card = number of turns to be able to complete the objective = n
        # after n turns, estimate our hand = hand', do hand' - required cards
        # convert that into a number


        self.actions = actions
        self.cost = cost
        # self.gain = gain

class StrategyExplorer(Strategy):

    current_objective: list[Action]

    def __init__(self):
        self.current_objective = []

    def play(self, board: Board, player: Player):
        if self.current_objective == []:
            actions = self._select_objective(board, player)
            self.current_objective = actions
            print(actions)

        self._do_objective(player)

    def _select_objective(self, board: Board, player: Player) -> list[Action]:
        assert self.current_objective == []
        o = ObjectiveBuildColony(board, player)
        o.do()
        return o.actions


    def _do_objective(self, player: Player):
        if self.current_objective is None:
            return

        i = 0
        for action in self.current_objective:
            if not action.available():
                breakpoint()
            assert action.available()
            if player.has_specified_resources(action.cost):
               action.apply()
               i += 1
            else:
                break
        self.current_objective = self.current_objective[i:]


