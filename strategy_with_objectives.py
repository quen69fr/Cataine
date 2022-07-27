from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from logs import log
from construction import ConstructionKind, NUM_CONSTRUCTION_MAX
from actions import Action, ActionBuildColony, ActionBuildRoad, ActionBuildTown
from board import Board
from tile_intersection import TileIntersection
from exchange import Exchange, BANK_PLAYER_FOR_EXCHANGE
from mark_functions_strategy_with_objectives import mark_intersection, mark_objective, mark_tile_thief
from resource_hand_count import ResourceHandCount
from strategy import Strategy

if TYPE_CHECKING:
    from player import Player


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
        # is there remaining colonies to build
        if self.player.num_colonies_belonging_to_player() >= NUM_CONSTRUCTION_MAX[ConstructionKind.COLONY]:
            return None
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

        num_roads_max = NUM_CONSTRUCTION_MAX[ConstructionKind.ROAD] - self.player.num_roads_belonging_to_player()
        q = starts
        while q:
            inter = q.pop(0)
            d = distances[inter] + 1
            # is there enough remaining roads to build
            if d > num_roads_max:
                break
            for path in inter.neighbour_paths:
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
        for inter, d in distances.items():
            if not inter.can_build():
                continue

            gain = mark_intersection(self.player, inter)
            cost = ResourceHandCount()
            cost.add(ActionBuildColony.cost)
            for _ in range(d):
                cost.add(ActionBuildRoad.cost)

            rank[inter] = mark_objective(self.player, cost, gain)
            if m is None or rank[inter] > rank[m]:
                m = inter
        if m is None:
            return []

        actions: list[Action] = [ActionBuildColony(m, self.player)]
        curr = m
        for i in range(distances[m]):
            for path, inter in curr.neighbour_paths_intersection():
                if path.road_player is None and inter in distances and distances[inter] == distances[curr] - 1:
                    actions.insert(0, ActionBuildRoad(path, self.player))
                    curr = inter
                    break

        self.actions = actions
        self.mark = rank[m]


class ObjectiveBuildTown(Objective):
    def do(self):
        # is there remaining towns to build
        if self.player.num_towns_belonging_to_player() >= NUM_CONSTRUCTION_MAX[ConstructionKind.TOWN]:
            return None
        rank: dict[TileIntersection, float] = {}
        m = None
        for inter in self.player.find_all_colonies_belonging_to_player():
            gain = mark_intersection(self.player, inter)
            cost = ResourceHandCount()
            cost.add(ActionBuildTown.cost)
            rank[inter] = mark_objective(self.player, cost, gain)
            if m is None or rank[inter] > rank[m]:
                m = inter
        if m is None:
            return []

        self.actions = [ActionBuildTown(m, self.player)]
        self.mark = rank[m]


class StrategyWithObjectives(Strategy):
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
            log(f"Objective: {obj}  -> mark: {obj.mark}")
            for action in obj.actions:
                if self.player.has_resources(action.cost):
                    assert action.available()
                    action.apply()
                else:
                    if self.exchange_with_others:
                        if self.player.exchanges is None:
                            return self._suggest_exchanges()
                        return True
                    else:
                        if self._exchange_with_the_bank():
                            return self.play()
                            # return False
                        return True
            obj = self._get_objective()
        return True

    def remove_cards_thief(self, num_cards_kept: int):
        best_resource_cards = None
        best_mark = 0
        old_hand = self.player.resource_cards
        for resource_cards in self.player.resource_cards.copy().subsets_of_size_k(num_cards_kept):
            self.player.resource_cards = resource_cards
            obj = self._get_objective()
            mark = 0 if obj is None else obj.mark
            if best_resource_cards is None or mark > best_mark:
                best_resource_cards = resource_cards
                best_mark = mark
        self.player.resource_cards = old_hand
        assert best_resource_cards is not None
        return best_resource_cards

    def move_thief(self):
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
            if player == self.player or player.num_resources() == 0:
                continue
            num_victory_points = player.num_victory_points()
            if best_player is None or num_victory_points > best_num_victory_points:
                best_player = player
                best_num_victory_points = num_victory_points
        assert best_player is not None
        return best_player

    def _suggest_exchanges(self) -> bool:
        obj = self._get_objective()
        cards_needed = ResourceHandCount()
        cards_useless = self.player.resource_cards.copy()
        for action in obj.actions:
            for res, num in action.cost.items():
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
                if mark > 1:
                    marked_exchanges.append((exchange, mark))

        if len(marked_exchanges) == 0:
            return True
        marked_exchanges.sort(key=lambda x: x[1], reverse=True)
        self.player.propose_exchanges([exchange for exchange, _ in marked_exchanges])
        return False

    def _exchange_with_the_bank(self):
        best_mark = 1
        best_exchange = None
        for exchange in self.player.get_all_possible_exchanges_with_the_bank():
            mark = self._mark_exchange(exchange)
            if mark > best_mark:
                best_mark = mark
                best_exchange = exchange
        if best_exchange is None:
            return False
        best_exchange.apply(self.player, BANK_PLAYER_FOR_EXCHANGE)
        return True

    def _mark_exchange(self, exchange: Exchange) -> float:
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
