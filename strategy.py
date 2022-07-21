from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from actions import Action, ActionBuildColony, ActionBuildRoad, ActionBuildTown
from board import Board
from tile import Tile
from tile_intersection import TileIntersection
from exchange import Exchange
from mark_functions_strategy import mark_intersection, mark_objective, mark_tile_thief
from resource_hand_count import ResourceHandCount

if TYPE_CHECKING:
    from player import Player


class Strategy:
    def __init__(self, board: Board, player: Player):
        self.board = board
        self.player = player

    @abstractmethod
    def play(self):
        pass


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
    def do(self, particular_starts: list[TileIntersection] = None):
        # find where my roads are
        starts = particular_starts
        if starts is None:
            starts = list(self.player.find_all_intersection_belonging_to_player())

            for path in self.player.find_all_path_belonging_to_player():
                for inter in path.intersections:
                    if inter.content is None and inter not in starts:
                        starts.append(inter)

        distances: dict[TileIntersection, int] = {}
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

            gain = mark_intersection(self.player, inte)
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
            gain = mark_intersection(self.player, inte)
            cost = ResourceHandCount()
            cost.add(ActionBuildTown.cost)
            rank[inte] = mark_objective(self.player, cost, gain)
            if m is None or rank[inte] > rank[m]:
                m = inte
        if m is None:
            return []

        self.actions = [ActionBuildTown(m, self.player)]
        self.mark = rank[m]


class StrategyExplorer(Strategy):
    def place_initial_colony(self):
        best_mark = 0
        best_inter = None
        for inter in self.board.intersections:
            if not inter.can_build():
                continue
            mark = mark_intersection(self.player, inter)
            if best_inter is None or best_mark < mark:
                best_inter = inter
                best_mark = mark

        return best_inter

    def place_road_around_initial_colony(self):
        inter = self.player.get_initial_colony_intersection_without_road()
        obj = ObjectiveBuildColony(self.board, self.player)
        obj.do(particular_starts=[inter])
        assert obj.actions
        action_road = obj.actions[0]
        assert isinstance(action_road, ActionBuildRoad)
        return action_road.path

    def play(self):
        obj = self._get_objective()
        while obj is not None:
            print("Objective:", obj, "  -> mark:", obj.mark)
            for action in obj.actions:
                if self.player.resource_cards.has(action.cost):
                    assert action.available()
                    action.apply()
                else:
                    if self.player.exchanges is None:
                        return self._suggest_exchanges()
                    return True
            obj = self._get_objective()
        return True

    def remove_cards_thief(self, num_cards_kept: int):
        best_resource_cards = None
        best_mark = 0
        for resource_cards in self.player.resource_cards.copy().subsets_of_size_k(num_cards_kept):
            self.player.resource_cards.add(resource_cards)
            obj = self._get_objective()
            mark = 0 if obj is None else obj.mark
            self.player.resource_cards.consume(resource_cards)
            if best_resource_cards is None or mark > best_mark:
                best_resource_cards = resource_cards
                best_mark = mark
        assert best_resource_cards is not None
        return best_resource_cards

    def move_thief(self) -> Tile:
        best_tile = None
        best_mark = None
        for tile in self.board.tiles:
            if tile == self.board.thief_tile:
                continue
            mark = mark_tile_thief(self.player, tile)
            if best_tile is None or mark > best_mark:
                best_tile = tile
                best_mark = mark
        assert best_tile is not None
        return best_tile

    def steal_card(self):
        best_player = None
        best_num_victory_points = 0
        for inter in self.board.thief_tile.intersections:
            if inter.content is None:
                continue
            player = inter.content.player
            if player == self.player or sum(player.resource_cards.values()) == 0:
                continue
            num_victory_points = player.num_victory_points()
            if best_player is None or num_victory_points > best_num_victory_points:
                best_player = player
                best_num_victory_points = num_victory_points
        assert best_player is not None
        return best_player

    def _suggest_exchanges(self):
        obj = self._get_objective()
        cards_needed = ResourceHandCount()
        cards_useless = self.player.resource_cards.copy()
        for res, num in obj.actions[0].cost.items():
            for _ in range(num):
                if not cards_useless.try_consume_one(res):
                    cards_needed.add_one(res)

        gains = list(cards_needed.subsets())

        marked_exchanges: list[tuple[Exchange, float]] = []
        for lost in cards_useless.subsets():
            if lost == ResourceHandCount():
                continue
            for gain in gains:
                if gain == ResourceHandCount():
                    continue
                exchange = Exchange(gain, lost)
                mark = self._mark_exchange(exchange)
                if mark > 0:
                    marked_exchanges.append((exchange, mark))

        if len(marked_exchanges) == 0:
            return True
        marked_exchanges.sort(key=lambda x: x[1], reverse=True)
        self.player.propose_exchanges([exchange for exchange, _ in marked_exchanges])
        return False

    def _mark_exchange(self, exchange: Exchange):
        if not exchange.possible(self.player):
            return 0
        obj_without_exchange = self._get_objective()
        exchange.apply_one(self.player)
        obj_with_exchange = self._get_objective()
        exchange.undo(self.player)
        if obj_without_exchange is None or obj_with_exchange is None:
            return 0  # end of the game...
        return obj_with_exchange.mark / obj_without_exchange.mark

    def accept_exchange(self, exchange: Exchange):
        return self._mark_exchange(exchange) > 1

    def _get_objective(self) -> Objective | None:
        objs = [ObjectiveBuildColony(self.board, self.player), ObjectiveBuildTown(self.board, self.player)]
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
