from __future__ import annotations

from typing import Generator
from resource import Resource
from typing import TYPE_CHECKING

import pygame

from actions import Action, ActionBuildRoad, ActionBuildColony, ActionBuildTown
from color import Color
from construction import Construction, ConstructionKind
from probability import get_expectation_of_intersection
from render_text import render_text
from strategy import StrategyChooseRandom, StrategyExplorer
from tile_intersection import TileIntersection

if TYPE_CHECKING:
    from board import Board


class Player:
    color: Color
    resource_cards: list[Resource]
    board: Board

    def __init__(self, color: Color, board: Board):
        self.color = color
        self.resource_cards: dict[Resource, int] = {
            Resource.CLAY: 0,
            Resource.WOOD: 0,
            Resource.WOOL: 0,
            Resource.HAY: 0,
            Resource.ROCK: 0
        }
        # self.dev_cards: list[DevCards] = []
        self.board = board
        self.strategy = StrategyExplorer()

    def play(self):
        all_group_actions = self.get_all_group_actions()
        print("Number of possibilities:", len(all_group_actions))
        group_actions = self.strategy.play(self.board, self, all_group_actions)
        print("Group action selected:", group_actions)
        for action in group_actions:
            action.apply()

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

    def get_all_one_shot_actions(self) -> list[Action]:
        if self.has_specified_resources(ActionBuildRoad.cost):
            yield from self._get_all_one_shot_action_build_road()
        if self.has_specified_resources(ActionBuildColony.cost):
            yield from self._get_all_one_shot_action_build_colony()
        if self.has_specified_resources(ActionBuildTown.cost):
            yield from self._get_all_one_shot_action_build_town()

    def _get_all_one_shot_action_build_road(self) -> Generator[Action]:
        for path in self.board.paths:
            action = ActionBuildRoad(path, self)
            if action.available():
                yield action

    def _get_all_one_shot_action_build_colony(self) -> Generator[Action]:
        for intersection in self.board.intersections:
            action = ActionBuildColony(intersection, self)
            if action.available():
                yield action

    def _get_all_one_shot_action_build_town(self) -> Generator[Action]:
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

    def add_resource_card(self, res: Resource):
        self.resource_cards[res] += 1

    def has_specified_resources(self, res: dict[Resource, int]):
        for res, count in res.items():
            if self.resource_cards[res] < count:
                return False
        return True

    def consume_resource_cards(self, cost: dict[Resource, int]):
        for res, count in cost.items():
            self.resource_cards[res] -= count
            assert self.resource_cards[res] >= 0

    def add_resource_cards(self, cost: dict[Resource, int]):
        for res, count in cost.items():
            self.resource_cards[res] += count

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
