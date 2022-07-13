from __future__ import annotations

from email.generator import Generator
from resource import Resource
from typing import TYPE_CHECKING

from actions import Action, ActionBuildRoad
from color import Color
from construction import ConstructionKind

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
