from __future__ import annotations

from typing import Generator
from resource import Resource, ResourceHandCount
from typing import TYPE_CHECKING

import pygame

from actions import Action, ActionBuildRoad, ActionBuildColony, ActionBuildTown
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
        # self.dev_cards: list[DevCards] = []
        self.board = board
        self.strategy = StrategyExplorer(self.board, self)

    def play(self, other_players: list[Player]):
        self.strategy.play(other_players)
        # all_group_actions = self.get_all_group_actions()
        # print("Number of possibilities:", len(all_group_actions))
        # group_actions = self.strategy.play(self.board, self, all_group_actions)
        # print("Group action selected:", group_actions)
        # for action in group_actions:
        #     action.apply()

    def get_all_group_actions(self) -> list[list[Action]]:
        def do():
            actions = []
            for action in self.get_all_one_shot_actions():
                action.apply()
                actions.append([action])
                group_actions = do()
                for group_action in group_actions:
                    group_action.insert(0, action)
                actions.extend(group_actions)
                action.undo()
            return actions

        groups_actions = do()
        groups_actions.append([])
        return groups_actions

    def get_all_one_shot_actions(self) -> Generator[Action, None, None]:
        if self.resource_cards.has(ActionBuildRoad.cost):
            yield from self._get_all_one_shot_action_build_road()
        if self.resource_cards.has(ActionBuildColony.cost):
            yield from self._get_all_one_shot_action_build_colony()
        if self.resource_cards.has(ActionBuildTown.cost):
            yield from self._get_all_one_shot_action_build_town()

    def _get_all_one_shot_action_build_road(self) -> Generator[Action, None, None]:
        for path in self.board.paths:
            action = ActionBuildRoad(path, self)
            if action.available():
                yield action

    def _get_all_one_shot_action_build_colony(self) -> Generator[Action, None, None]:
        for intersection in self.board.intersections:
            action = ActionBuildColony(intersection, self)
            if action.available():
                yield action

    def _get_all_one_shot_action_build_town(self) -> Generator[Action, None, None]:
        for intersection in self.board.intersections:
            action = ActionBuildTown(intersection, self)
            if action.available():
                yield action

    def place_initial_colony(self):
        best = None
        for intersection in self.board.intersections:
            if best is None \
                    or intersection.can_build() \
                    and neighbour_tiles_expectation(best) < neighbour_tiles_expectation(intersection):
                best = intersection

        assert best.content is None
        best.content = Construction(kind=ConstructionKind.COLONY, player=self)

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

    def get_resource_production_expectation_without_exchange(self):
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
                if tile.resource == Resource.DESERT:
                    continue
                prod[tile.resource] += get_probability_to_roll(tile.dice_number) * c

        return prod

    def get_resource_production_in_number_of_turns_with_systematic_exchange(self):
        """ resource -> number of turns """
        prod_turns = {}
        prod = self.get_resource_production_expectation_without_exchange()
        min_number_of_turns_with_exchange = 4 / max(prod.values())
        for res, proba in prod.items():
            if proba == 0:
                prod_turns[res] = min_number_of_turns_with_exchange
            else:
                prod_turns[res] = min(1/proba, min_number_of_turns_with_exchange)

        return prod_turns

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

    def get_ports(self) -> Generator[Resource]:
        for path in self.board.paths:
            if path.port is not None and (
                    path.intersections[0].content is not None and path.intersections[0].content.player == self or
                    path.intersections[1].content is not None and path.intersections[1].content.player == self):
                yield path.port


def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(
        t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)
