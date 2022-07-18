from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from actions import Action, ActionBuildColony, ActionBuildRoad, ActionBuildTown
from board import Board
from tile_intersection import TileIntersection
from exchange import Exchange, BANK_PLAYER_FOR_EXCHANGE

if TYPE_CHECKING:
    from player import Player

from resource import Resource, ResourceHandCount


class Strategy:
    def __init__(self, board: Board, player: Player):
        self.board = board
        self.player = player

    @abstractmethod
    def play(self, other_players: list[Player]):
        pass


# class StrategyChooseRandom(Strategy):

#     def play(self, board: Board, player: Player, all_actions: list[list[Action]]) -> list[Action]:
#         result = random.choice(all_actions)
#         return result

class Objective:
    def __init__(self, board: Board, player: Player) -> None:
        self.board = board
        self.player = player

        self.actions = []
        self.mark = None

    @abstractmethod
    def do(self):
        pass


class ObjectiveBuildColony(Objective):
    def do(self):
        # find where my roads are
        starts = list(self.player.find_all_intersection_belonging_to_player())
        distances: dict[TileIntersection, int] = {}

        for path in self.player.find_all_path_belonging_to_player():
            for inter in path.intersections:
                if inter.content is None and inter not in starts:
                    starts.append(inter)

        for start in starts:
            distances[start] = 0

        q = starts
        while q:
            inte = q.pop(0)
            d = distances[inte] + 1
            for path in inte.neighbour_paths:
                if path.road_player is not None:
                    continue
                for neigh in path.intersections:
                    if neigh.content is None and neigh not in distances:
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
        for i in range(distances[m]):
            for path, inte in curr.neighbour_paths_intersection():
                if path.road_player is None and inte in distances and distances[inte] == distances[curr] - 1:
                    actions.insert(0, ActionBuildRoad(path, self.player))
                    curr = inte
                    break

        self.actions = actions
        self.mark = rank[m]


class ObjectiveBuildTown(Objective):
    def do(self):
        rank: dict[TileIntersection, float] = {}
        m = None
        for inte in self.player.find_all_colonies_belonging_to_player():
            gain = 6 * inte.neighbour_tiles_expectation()
            cost = ResourceHandCount()
            cost.add(ActionBuildTown.cost)
            rank[inte] = mark_objective(self.player, cost, gain)
            if m is None or rank[inte] > rank[m]:
                m = inte
        if m is None:
            return []

        self.actions = [ActionBuildTown(m, self.player)]
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

    gain = 200 * initial_gain
    for res, count in hand_after_cost_num_turns.items():
        gain += count * prod_turns[res]
    return gain / (cost_num_turns + 1)


class StrategyExplorer(Strategy):
    def play(self, other_players: list[Player]):
        obj = self._get_objective()
        while obj is not None:
            for action in obj.actions:
                if self.player.resource_cards.has(action.cost):
                    assert action.available()
                    action.apply()
                else:
                    if self._suggest_and_make_exchanges(other_players):
                        self.play(other_players)
                    return
            obj = self._get_objective()

    def _suggest_and_make_exchanges(self, other_players: list[Player]):
        obj = self._get_objective()
        cards_needed = ResourceHandCount()
        cards_useless = self.player.resource_cards.copy()
        for res, num in obj.actions[0].cost.items():
            for _ in range(num):
                if not cards_useless.try_consume_one(res):
                    cards_needed.add_one(res)
        best_mark = 1
        best_exchange = None
        best_player_for_exchange = None
        for lost in cards_useless.copy().subsets():
            if lost == ResourceHandCount():
                continue
            for gain in cards_needed.copy().subsets():
                if gain == ResourceHandCount():
                    continue
                exchange = Exchange(gain, lost)
                mark = self._mark_exchange(exchange)
                if mark > best_mark:
                    player = self._ask_every_one_for_exchange(exchange, other_players)
                    if player is not None:
                        best_mark = mark
                        best_exchange = exchange
                        best_player_for_exchange = player
        if best_exchange is None:
            return False
        print(" -> Exchange:", best_exchange, "with", best_player_for_exchange)
        best_exchange.apply(self.player, best_player_for_exchange)
        return True

    def _ask_every_one_for_exchange(self, exchange: Exchange, other_players: list[Player]) -> \
            Player | BANK_PLAYER_FOR_EXCHANGE | None:
        # We look for the ports
        ports = list(self.player.get_ports())
        if Resource.P_3_FOR_1 in ports and 3 * sum(exchange.gain.values()) == sum(exchange.lost.values()):
            possible = True
            for _, num in exchange.lost:
                if not num % 3 == 0:
                    possible = False
                    break
            if possible:
                return BANK_PLAYER_FOR_EXCHANGE
        if 2 * sum(exchange.gain.values()) == sum(exchange.lost.values()):
            possible = True
            for res, num in exchange.lost:
                if not (num % 2 == 0 and (num == 0 or res in ports)):
                    possible = False
                    break
            if possible:
                return BANK_PLAYER_FOR_EXCHANGE

        # We ask the other players
        for player in other_players:
            if player.strategy.accept_exchange(exchange.inverse()):
                return player

    def _mark_exchange(self, exchange: Exchange):
        if not exchange.possible(self.player):
            return -1
        mark_without_exchange = self._get_objective().mark
        exchange.apply_one(self.player)
        mark_with_exchange = self._get_objective().mark
        exchange.undo(self.player)
        return mark_with_exchange / mark_without_exchange

    def accept_exchange(self, exchange: Exchange):
        return self._mark_exchange(exchange) > 1

    def _get_objective(self) -> Objective | None:
        objs = [ObjectiveBuildColony(self.board, self.player), ObjectiveBuildTown(self.board, self.player)]
        # objs = [ObjectiveBuildColony(self.board, self.player)]
        best_obj: Objective | None = None
        for obj in objs:
            obj.do()
            if not obj.actions:
                continue
            if best_obj is None or best_obj.mark < obj.mark:
                best_obj = obj
        if best_obj is None:
            return None
        return best_obj
