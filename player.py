from __future__ import annotations

from typing import Generator, TYPE_CHECKING
from abc import abstractmethod

import pygame

from constants import NUM_CARD_MAX_THIEF
from resource import Resource
from resource_hand_count import ResourceHandCount
from dev_cards import DevCard
from color import Color
from construction import Construction, ConstructionKind
from probability import get_expectation_of_intersection, get_probability_to_roll
from rendering_functions import render_text
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath
from exchange import Exchange

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
        self.dev_cards_revealed: list[DevCard] = []
        self.board = board

        self.num_cards_to_remove_for_thief = 0
        self.exchanges: None | list[Exchange] = None
        self.exchange_asked: Exchange | None = None
        self.exchange_accepted = False

    def place_initial_colony(self, intersection: TileIntersection):
        intersection.content = Construction(kind=ConstructionKind.COLONY, player=self)

        if self.num_colonies_belonging_to_player() == 2:
            for tile in intersection.neighbour_tiles:
                if not tile.resource == Resource.DESERT:
                    self.resource_cards.add_one(tile.resource)

    def place_initial_road(self, path: TilePath):
        path.road_player = self

    def move_thief_match_num_cards(self):
        num_cards = sum(self.resource_cards.values())
        if num_cards > NUM_CARD_MAX_THIEF:
            self.num_cards_to_remove_for_thief = num_cards // 2

    def remove_cards_for_thief(self, new_resource_hand_cards: ResourceHandCount):
        self.resource_cards = new_resource_hand_cards
        self.num_cards_to_remove_for_thief = 0

    def move_thief(self, tile: Tile):
        self.board.thief_tile = tile

    def steal_card(self, player: Player | None):
        res = player.resource_cards.random_resource()
        self.resource_cards.add_one(res)
        player.resource_cards.try_consume_one(res)

    def can_steal(self):
        for inter in self.board.thief_tile.intersections:
            if inter.content is None:
                continue
            player = inter.content.player
            if not player == self and not sum(player.resource_cards.values()) == 0:
                return True
        return False

    def propose_exchanges(self, exchanges: list[Exchange]):
        self.exchanges = exchanges

    def accept_exchange(self):
        self.exchange_accepted = True

    def reject_exchange(self):
        self.exchange_asked = None

    def ask_for_exchange(self, exchange: Exchange):
        if self.has_resources_to_exchange(exchange):
            self.exchange_asked = exchange
            self.exchange_accepted = False
            return True
        return False

    def exchange_asked_done(self):
        self.exchange_asked = None
        self.exchange_accepted = False

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

    def get_resource_production_expectation_without_exchange(self, with_thief: bool = False):
        """ resource -> number of that resource per turn """
        prod: dict[Resource, float] = {
            Resource.CLAY: 0,
            Resource.WOOD: 0,
            Resource.WOOL: 0,
            Resource.HAY: 0,
            Resource.ROCK: 0
        }

        for inte in self.find_all_intersection_belonging_to_player():
            assert inte.content is not None
            if inte.content.kind == ConstructionKind.COLONY:
                c = 1
            else:
                c = 2
            for tile in inte.neighbour_tiles:
                if tile.resource == Resource.DESERT or (with_thief and self.board.thief_tile == tile):
                    continue
                prod[tile.resource] += get_probability_to_roll(tile.dice_number) * c

        return prod

    def get_resource_production_in_number_of_turns_with_systematic_exchange(self, with_thief: bool = False):
        """ resource -> number of turns """
        prod_turns = {}
        prod = self.get_resource_production_expectation_without_exchange(with_thief)
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

    def num_victory_points(self):
        # TODO : Longest road and knights
        num = 0
        for inter in self.board.intersections:
            if inter.content is not None and inter.content.player == self:
                num += 1
                if inter.content.kind == ConstructionKind.TOWN:
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

    def has_resources_to_exchange(self, exchange: Exchange):
        return self.resource_cards.has(exchange.lost)

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

    def __repr__(self):
        return f"<Player {self.color.name}>"
    
    def __str__(self):
        return repr(self)

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


def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(
        t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)
