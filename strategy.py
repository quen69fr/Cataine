from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from actions import Action, ActionBuildColony, ActionBuildRoad
from board import Board
from tile_intersection import TileIntersection

if TYPE_CHECKING:
    from player import Player

from resource import Resource, ResourceHandCount


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
        self.mark = None

    def do(self):
        # find where my roads are
        starts = list(self.player.find_all_intersection_belonging_to_player())
        distances: dict[TileIntersection, int] = {}

        for path in self.player.find_all_path_belonging_to_player():
            if path.intersections[0] not in starts:
                starts.append(path.intersections[0])
            if path.intersections[1] not in starts:
                starts.append(path.intersections[1])

        for start in starts:
            distances[start] = 0

        q = starts
        while q:
            inte = q.pop(0)
            d = distances[inte] + 1
            for path in inte.neighbour_paths:
                for neigh in path.intersections:
                    if neigh not in distances:
                        distances[neigh] = d
                        q.append(neigh)

        # rank all intersections
        # select the best one and do it

        rank: dict[TileIntersection, float] = {}
        m = None
        for inte, d in distances.items():
            if not inte.can_build():
                continue

            gain = 6 * inte.neighbour_tiles_expectation()
            gain = 100 * gain ** 10
            # gain = 0
            cost = ResourceHandCount()
            cost.add(ActionBuildColony.cost)
            for _ in range(d):
                cost.add(ActionBuildRoad.cost)

            rank[inte] = mark_objective(self.player, cost, gain)
            if m is None or rank[inte] > rank[m]:
                m = inte
        if m is None:
            return []

        actions: list[Action] = [ActionBuildColony(m, self.player)]
        curr = m
        cost = ResourceHandCount()
        cost.add(ActionBuildColony.cost)
        for i in range(distances[m]):
            for path, inte in curr.neighbour_paths_intersection():
                if path.road_player is None and distances[inte] == distances[curr] - 1:
                    actions.insert(0, ActionBuildRoad(path, self.player))
                    cost.add(ActionBuildRoad.cost)
                    curr = inte
                    break

        self.actions = actions
        self.mark = rank[m]


def mark_objective(player: Player, cost_no_modify: ResourceHandCount, initial_gain: float) -> float:
    cost = cost_no_modify.copy()
    required_cards = cost.copy()

    # breakpoint()

    prod_turns = player.get_resource_production_in_number_of_turns_with_systematic_exchange()

    cost.subtract_fine_if_not_present(player.resource_cards)
    cost_num_turns = max(num * prod_turns[res] for res, num in cost.items())

    # build list of required cards - current hand
    # max of the inverse probabilities for each card = number of turns to be able to complete the objective = n
    # after n turns, estimate our hand = hand', do hand' - required cards
    # convert that into a number

    # add cards in the current hand
    hand_after_cost_num_turns: dict[Resource, float] = {}
    for res, count in player.resource_cards.items():
        hand_after_cost_num_turns[res] = count

    # predict cards and add to future hands
    for res, expectation in player.get_resource_production_expectation_without_exchange().items():
        hand_after_cost_num_turns[res] += expectation * cost_num_turns

    # remove all resources that will be used by this objective
    for res, count in required_cards.items():
        hand_after_cost_num_turns[res] -= count
        # assert hand_after_cost_num_turns[res] >= 0

    gain = initial_gain
    for res, count in hand_after_cost_num_turns.items():
        gain += count * prod_turns[res]
    return gain / (cost_num_turns + 1)


class StrategyExplorer(Strategy):
    current_objective: list[Action]

    def __init__(self):
        self.current_objective = []

    def play(self, board: Board, player: Player):
        if not self.current_objective:
            actions = self._select_objective(board, player)
            self.current_objective = actions

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
            if player.resource_cards.has(action.cost):
                action.apply()
                i += 1
            else:
                break
        self.current_objective = self.current_objective[i:]
