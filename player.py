from __future__ import annotations

from typing import Generator
from typing import TYPE_CHECKING

import pygame

from constants import NUM_CARD_MAX_THIEF
from resource import Resource, ResourceHandCount
from dev_cards import DevCard
from color import Color
from construction import Construction, ConstructionKind
from probability import get_expectation_of_intersection, get_probability_to_roll
from render_text import render_text
from strategy import StrategyExplorer
from tile_intersection import TileIntersection
from tile_path import TilePath

if TYPE_CHECKING:
    from board import Board


class Player:
    color: Color
    resource_cards: ResourceHandCount
    board: Board

    def __init__(self, color: Color, board: Board):
        self.color = color
        self.resource_cards = ResourceHandCount()
        self.dev_cards: list[DevCard] = []
        self.dev_cards_revealed: list[DevCard] = []
        self.board = board
        self.strategy = StrategyExplorer(self.board, self)

    def play(self, other_players: list[Player]):
        self.strategy.play(other_players)

    def place_initial_colony(self, take_resources: bool = False):
        self.strategy.place_initial_colony(take_resources)

    def remove_cards_for_thief(self):
        num_cards = sum(self.resource_cards.values())
        if num_cards > NUM_CARD_MAX_THIEF:
            self.strategy.remove_cards_thief((num_cards + 1) // 2)

    def move_thief(self):
        self.strategy.move_thief()

    def steal_card(self):
        self.strategy.steal_card()

    def find_all_intersection_belonging_to_player(self) -> Generator[TileIntersection, None, None]:
        for inte in self.board.intersections:
            if inte.content is not None and inte.content.player == self:
                yield inte

    def find_all_colonies_belonging_to_player(self) -> Generator[TileIntersection, None, None]:
        for inte in self.board.intersections:
            if inte.content == Construction(ConstructionKind.COLONY, self):
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
        num = 0
        for inter in self.board.intersections:
            if inter.content is not None and inter.content.player == self:
                num += 1
                if inter.content.kind == ConstructionKind.TOWN:
                    num += 1
        return num

    def __repr__(self):
        return f"<Player {self.color.name}>"
    
    def __str__(self):
        return repr(self)

    def render(self, screen: pygame.Surface, x0: int, y0: int, my_turn: bool):
        if my_turn:
            screen.fill((0, 0, 0), (x0 - 5, y0 - 5, 240, 290))
        screen.fill(self.color.value, (x0, y0, 230, 280))
        screen.fill((255, 255, 255), (x0 + 5, y0 + 5, 220, 270))
        x = x0 + 15
        y = y0 + 80
        for res, num in self.resource_cards.items():
            render_text(screen, f"{res}: {num}", x, y, 30, (0, 0, 0), False)
            y += 40


def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(
        t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)
