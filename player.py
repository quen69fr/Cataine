from __future__ import annotations

from typing import Generator, TYPE_CHECKING
from abc import abstractmethod

import pygame

from constants import NUM_CARD_MAX_THIEF, SIZE_MIN_LARGEST_ARMY, LENGTH_MIN_LONGEST_ROAD
from resource import Resource
from resource_hand_count import ResourceHandCount, get_all_possible_set_of_resources
from dev_cards import DevCard, ORDER_DEV_CARD
from color import Color
from construction import Construction, ConstructionKind
from probability import get_probability_to_roll
from rendering_functions import render_text
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath
from exchange import Exchange
from actions import Action, ActionBuildColony, ActionBuildRoad, ActionBuildTown, ActionBuyDevCard, ActionRevealDevCard

if TYPE_CHECKING:
    from board import Board


class Player:
    color: Color
    resource_cards: ResourceHandCount
    board: Board

    def __init__(self, nickname: str, color: Color, board: Board):
        self.nickname = nickname
        self.color = color
        self.resource_cards = ResourceHandCount()
        self.dev_cards: list[DevCard] = []
        self.num_dev_cards_just_bought: int = 0
        self.dev_cards_revealed: list[DevCard] = []
        self.board = board
        self.board.players_longest_road.append(self)

        self.num_cards_to_remove_for_thief = 0
        self.dev_card_in_action: None | DevCard = None
        self.exchanges: None | list[Exchange] = None
        self.exchange_asked: Exchange | None = None
        self.exchange_accepted = False
        self.monopoly_resource: None | Resource = None
        self.length_longest_road: int = 0

        self.production_expectation: dict[Resource, float] = {
            Resource.CLAY: 0,
            Resource.WOOD: 0,
            Resource.WOOL: 0,
            Resource.HAY: 0,
            Resource.ROCK: 0
        }

    def add_road(self, path: TilePath):
        path.road_player = self
        self.update_longest_road()

    def add_colony(self, intersection: TileIntersection):
        intersection.content = Construction(ConstructionKind.COLONY, self)
        # Check if we cut the longest road
        player = None
        for path in intersection.neighbour_paths:
            if path.road_player is None or path.road_player == self:
                continue
            if player is None:
                player = path.road_player
                continue
            if player == path.road_player:
                player.update_longest_road()
        self.update_production_expectations(intersection)

    def add_town(self, intersection: TileIntersection):
        intersection.content = Construction(ConstructionKind.TOWN, self)
        self.update_production_expectations(intersection)

    def update_production_expectations(self, new_intersection: TileIntersection):
        for tile in new_intersection.neighbour_tiles:
            if tile.resource == Resource.DESERT:
                continue
            self.production_expectation[tile.resource] += get_probability_to_roll(tile.dice_number)

    def add_resources(self, resources: ResourceHandCount):
        self.resource_cards.add(resources)

    def consume_resources(self, resources: ResourceHandCount):
        self.resource_cards.consume(resources)

    def add_one_resource(self, res: Resource, num: int = 1):
        self.resource_cards.add_one(res, num=num)

    def try_consume_one(self, res: Resource):
        return self.resource_cards.try_consume_one(res)

    def has_resources(self, cost: ResourceHandCount):
        return self.resource_cards.has(cost)

    def num_resources(self):
        return self.resource_cards.num_resources()

    def reveal_dev_card(self, dev_card: DevCard):
        self.dev_cards.remove(dev_card)
        self.dev_cards_revealed.append(dev_card)
        self.dev_card_in_action = dev_card
        # Check for the largest army
        if dev_card == DevCard.KNIGHT and not self.board.player_largest_army == self:
            size_army = self.num_knights()
            if size_army >= SIZE_MIN_LARGEST_ARMY:
                if self.board.player_largest_army is None or self.board.player_largest_army.num_knights() < size_army:
                    self.board.player_largest_army = self

    def place_initial_colony(self, intersection: TileIntersection):
        self.add_colony(intersection)
        # Add cards
        if self.num_colonies_belonging_to_player() == 2:
            for tile in intersection.neighbour_tiles:
                if not tile.resource == Resource.DESERT:
                    self.add_one_resource(tile.resource)

    def place_initial_road(self, path: TilePath):
        self.add_road(path)

    def move_thief_match_num_cards(self):
        num_cards = self.num_resources()
        if num_cards > NUM_CARD_MAX_THIEF:
            self.num_cards_to_remove_for_thief = num_cards // 2

    def remove_cards_for_thief(self, new_resource_hand_cards: ResourceHandCount):
        self.resource_cards = new_resource_hand_cards
        self.num_cards_to_remove_for_thief = 0

    def move_thief(self, tile: Tile):
        self.board.thief_tile = tile

    def steal_card(self, player: Player | None):
        res = player.resource_cards.random_resource()
        self.add_one_resource(res)
        player.try_consume_one(res)

    def can_steal(self):
        for inter in self.board.thief_tile.intersections:
            if inter.content is None:
                continue
            player = inter.content.player
            if not player == self and not player.num_resources() == 0:
                return True
        return False

    def can_steal_player(self, player: Player):
        if player == self or player.num_resources() == 0:
            return False
        for inter in self.board.thief_tile.intersections:
            if inter.content is None:
                continue
            if player == inter.content.player:
                return True
        return False

    def propose_exchanges(self, exchanges: list[Exchange]):
        self.exchanges = exchanges

    def accept_exchange(self):
        self.exchange_accepted = True

    def reject_exchange(self):
        self.exchange_asked = None

    def ask_for_exchange(self, exchange: Exchange):
        if self.has_resources(exchange.lost):
            self.exchange_asked = exchange
            self.exchange_accepted = False
            return True
        return False

    def exchange_asked_done(self):
        self.exchange_asked = None
        self.exchange_accepted = False

    def monopoly(self, resource: Resource):
        self.monopoly_resource = resource

    def end_turn(self):
        self.num_dev_cards_just_bought = 0

    # ------------------------------------------------------------------------------------------------

    def find_all_intersection_belonging_to_player(self) -> Generator[TileIntersection, None, None]:
        for inte in self.board.intersections:
            if inte.content is not None and inte.content.player == self:
                yield inte

    def find_all_colonies_belonging_to_player(self) -> Generator[TileIntersection, None, None]:
        for inte in self.board.intersections:
            if inte.content == Construction(ConstructionKind.COLONY, self):
                yield inte

    def find_all_towns_belonging_to_player(self) -> Generator[TileIntersection, None, None]:
        for inte in self.board.intersections:
            if inte.content == Construction(ConstructionKind.TOWN, self):
                yield inte

    def find_all_path_belonging_to_player(self) -> Generator[TilePath, None, None]:
        for path in self.board.paths:
            if path.road_player == self:
                yield path

    def get_resource_production_expectation_with_thief(self) -> dict[Resource, float]:
        if self.board.thief_tile.resource == Resource.DESERT:
            return self.production_expectation
        prod = self.production_expectation.copy()
        expect = get_probability_to_roll(self.board.thief_tile.dice_number)
        for inter in self.board.thief_tile.intersections:
            if inter.content is not None and inter.content.player == self:
                prod[self.board.thief_tile.resource] += \
                    expect * (1 if inter.content.kind == ConstructionKind.COLONY else 2)
        return prod

    def get_resource_production_in_number_of_turns_with_systematic_exchange(self, with_thief: bool = False) \
            -> dict[Resource, float]:
        prod_turns = {}
        prod = self.get_resource_production_expectation_with_thief() if with_thief else self.production_expectation
        min_number_of_turns_with_exchange = 4 / max(prod.values())
        for res, proba in prod.items():
            if proba == 0:
                prod_turns[res] = min_number_of_turns_with_exchange
            else:
                prod_turns[res] = min(1/proba, min_number_of_turns_with_exchange)

        return prod_turns

    def get_ports(self) -> Generator[Resource]:
        for path in self.board.paths:
            if path.port is not None and (
                    path.intersections[0].content is not None and path.intersections[0].content.player == self or
                    path.intersections[1].content is not None and path.intersections[1].content.player == self):
                yield path.port.resource

    def get_all_possible_exchanges_with_the_bank(self) -> Generator[Exchange]:
        ports = list(self.get_ports())
        n_min = 3 if Resource.P_3_FOR_1 in ports else 4
        hand_abstract_exchange = ResourceHandCount()
        hand_abstract_multiplication = ResourceHandCount()
        for res, num in self.resource_cards.items():
            if res in ports:
                n = 2
            else:
                n = n_min
            hand_abstract_exchange[res] = num // n
            hand_abstract_multiplication[res] = n

        for i in range(1, 1 + hand_abstract_exchange.num_resources()):
            for gain in get_all_possible_set_of_resources(i):
                for lost in hand_abstract_exchange.subsets_of_size_k(i):
                    intelligent = True
                    for res, num in lost.items():
                        if num == 0:
                            continue
                        else:
                            if not gain[res] == 0:
                                intelligent = False
                                break
                            lost[res] *= hand_abstract_multiplication[res]
                    if intelligent:
                        yield Exchange(gain, lost)

    def num_bonus_victory_points(self) -> int:
        num = 0
        if self.length_longest_road >= LENGTH_MIN_LONGEST_ROAD and self.board.players_longest_road[0] == self:
            num += 2
        if self.board.player_largest_army == self:
            num += 2
        return num

    def num_victory_points(self, without_longest_road_and_largest_army: bool = False) -> int:
        num = 0
        if not without_longest_road_and_largest_army:
            num += self.num_bonus_victory_points()
        for inter in self.board.intersections:
            if inter.content is not None and inter.content.player == self:
                num += 1
                if inter.content.kind == ConstructionKind.TOWN:
                    num += 1
        for dev_card in self.dev_cards_revealed:
            if dev_card == DevCard.VICTORY_POINT:
                num += 1
        return num

    def num_knights(self):
        n = 0
        for dev_card in self.dev_cards_revealed:
            if dev_card == DevCard.KNIGHT:
                n += 1
        return n

    def num_roads_belonging_to_player(self):
        n = 0
        for path in self.board.paths:
            if path.road_player == self:
                n += 1
        return n

    def num_colonies_belonging_to_player(self):
        n = 0
        for inte in self.board.intersections:
            if inte.content == Construction(ConstructionKind.COLONY, self):
                n += 1
        return n

    def num_towns_belonging_to_player(self):
        n = 0
        for inte in self.board.intersections:
            if inte.content == Construction(ConstructionKind.TOWN, self):
                n += 1
        return n

    def num_constructions_belonging_to_player(self, kind: ConstructionKind):
        if kind == ConstructionKind.ROAD:
            return self.num_roads_belonging_to_player()
        elif kind == ConstructionKind.COLONY:
            return self.num_colonies_belonging_to_player()
        elif kind == ConstructionKind.TOWN:
            return self.num_towns_belonging_to_player()

    def get_initial_colony_intersection_without_road(self) -> TileIntersection:
        for inter in self.board.intersections:
            if inter.content == Construction(ConstructionKind.COLONY, self):
                has_roads = False
                for path in inter.neighbour_paths:
                    if path.road_player is not None:
                        has_roads = True
                        break
                if not has_roads:
                    return inter
        assert False

    def can_exchange_with_the_bank(self, exchange: Exchange) -> bool:
        # We look for the ports
        ports = list(self.get_ports())
        # 2 for 1
        if 2 * sum(exchange.gain.values()) == sum(exchange.lost.values()):
            possible = True
            for res, num in exchange.lost:
                if not (num % 2 == 0 and (num == 0 or res in ports)):
                    possible = False
                    break
            if possible:
                return True

        # 3 for 1
        if Resource.P_3_FOR_1 in ports and 3 * sum(exchange.gain.values()) == sum(exchange.lost.values()):
            possible = True
            for _, num in exchange.lost:
                if not num % 3 == 0:
                    possible = False
                    break
            if possible:
                return True
        # 4 for 1
        if 4 * sum(exchange.gain.values()) == sum(exchange.lost.values()):
            possible = True
            for _, num in exchange.lost:
                if not num % 4 == 0:
                    possible = False
                    break
            if possible:
                return True
        return False

    def get_length_longest_road(self):
        def get_all_possible_length_from_intersection(intersection: TileIntersection, remaining_paths: set[TilePath]):
            if len(remaining_paths) == 0:
                return 0
            better_length = 0
            for path in intersection.neighbour_paths:
                if path in remaining_paths:
                    next_intersection = path.intersections[1 if path.intersections[0] == intersection else 0]
                    length = 1
                    if next_intersection.content is None or next_intersection.content.player == self:
                        remaining_paths.remove(path)
                        length += get_all_possible_length_from_intersection(next_intersection, remaining_paths)
                        remaining_paths.add(path)
                    better_length = max(length, better_length)
            return better_length

        paths_set = set(self.find_all_path_belonging_to_player())
        if len(paths_set) == 0:
            return 0
        intersection_set = set()
        for path_i in paths_set:
            for inter in path_i.intersections:
                intersection_set.add(inter)
        return max(get_all_possible_length_from_intersection(inter, paths_set) for inter in intersection_set)

    def update_longest_road(self):
        length = self.get_length_longest_road()
        if not length == self.length_longest_road:
            self.length_longest_road = length
            self.board.update_longest_road(self)

    def get_all_possible_one_shot_actions(self, include_dev_card: bool = True) -> Generator[Action]:
        if self.has_resources(ActionBuildColony.cost):
            for inter in self.board.intersections:
                action = ActionBuildColony(inter, self)
                if action.available():
                    yield action

        if self.has_resources(ActionBuildTown.cost):
            for inter in self.board.intersections:
                action = ActionBuildTown(inter, self)
                if action.available():
                    yield action

        if self.has_resources(ActionBuildRoad.cost):
            for path in self.board.paths:
                action = ActionBuildRoad(path, self)
                if action.available():
                    yield action

        if include_dev_card:
            if self.has_resources(ActionBuyDevCard.cost):
                yield ActionBuyDevCard(self)

            for dev in ORDER_DEV_CARD:
                action = ActionRevealDevCard(dev, self)
                if action.available():
                    yield action

    def __repr__(self):
        return f"<Player {self.color.name}>"

    def __str__(self):
        return repr(self)

    # ------------------------------------------------------------------------------------------------

    def render_draft(self, screen: pygame.Surface, x0: int, y0: int, my_turn: bool):
        if my_turn:
            screen.fill((0, 0, 0), (x0 - 5, y0 - 5, 240, 290))
        screen.fill(self.color.value, (x0, y0, 230, 280))
        screen.fill((255, 255, 255), (x0 + 5, y0 + 5, 220, 270))
        x = x0 + 15
        y = y0 + 80
        for res, num in self.resource_cards.items():
            render_text(screen, f"{res}: {num}", x, y, 30, (0, 0, 0), False)
            y += 40


class PlayerManager:
    def __init__(self, player: Player):
        self.player = player

    @abstractmethod
    def play(self) -> bool:
        pass

    @abstractmethod
    def place_initial_colony(self) -> bool:
        pass

    @abstractmethod
    def place_initial_road(self) -> bool:
        pass

    @abstractmethod
    def remove_cards_for_thief(self) -> bool:
        pass

    @abstractmethod
    def move_thief(self) -> bool:
        pass

    @abstractmethod
    def steal_card(self) -> bool:
        pass

    @abstractmethod
    def accept_exchange(self) -> bool:
        pass

    @abstractmethod
    def throw_dice(self) -> bool:
        pass

    @abstractmethod
    def get_resources(self) -> bool:
        pass

    @abstractmethod
    def place_free_road(self) -> bool:
        pass

    @abstractmethod
    def free_card(self) -> bool:
        pass

    @abstractmethod
    def monopoly(self) -> bool:
        pass
