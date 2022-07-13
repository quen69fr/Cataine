from __future__ import annotations

from cmath import exp
from email.generator import Generator
from resource import Resource
from typing import TYPE_CHECKING

from actions import Action, ActionBuildRoad
from color import Color
from construction import Construction, ConstructionKind
from probability import get_expectation_of_intersection
from tile_intersection import TileIntersection

if TYPE_CHECKING:
    from board import Board


class Player:
    color: Color
    resource_cards: list[Resource]
    board: Board

    def __init__(self, color: Color, board: Board):
        self.color = color
        self.resource_cards: list[Resource] = []
        # self.dev_cards: list[DevCards] = []
        self.board = board

    def play(self):
        self.strategy.play(self.get_all_group_actions())

    def get_all_group_actions(self) -> list[Action]:
        def do():
            actions = []
            for action in self.get_all_one_shot_actions():
                action.apply()
                group_actions = do()
                for group_action in group_actions:
                    group_action.insert(0, action)
                actions.extend(group_actions)
                action.undo()
            return actions
        group_actions = do()
        group_actions.append([])
        return group_actions

    def get_all_one_shot_actions(self) -> list[Action]:
        if self.has_enough_resources_to_build(ConstructionKind.ROAD):
            yield from self._get_all_one_shot_action_build_road()

    def _get_all_one_shot_action_build_road(self) -> Generator[Action]:
        for path in self.board.paths:
            action = ActionBuildRoad(path, self)
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

def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)

