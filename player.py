from __future__ import annotations

from cmath import exp
from collections import defaultdict
from curses import has_key
from email.generator import Generator
from resource import Resource
from typing import TYPE_CHECKING

from actions import Action, ActionBuildRoad
from color import Color
from construction import Construction, ConstructionKind
from probability import get_expectation_of_intersection
from strategy import StrategyChooseRandom
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
        self.strategy = StrategyChooseRandom()

    def play(self):
        print(self, "resources", self.resource_cards)
        group_actions = self.strategy.play(self.board, self, self.get_all_group_actions())
        print("selected:", group_actions)
        for action in group_actions:
            action.apply()
            
    def get_all_group_actions(self) -> list[Action]:

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

        group_actions = do()
        group_actions.append([])
        return group_actions

    def get_all_one_shot_actions(self) -> list[Action]:
        if self.has_specified_resources(ActionBuildRoad.cost):
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
        

def neighbour_tiles_expectation(intersection: TileIntersection):
    return get_expectation_of_intersection(t.dice_number for t in intersection.neighbour_tiles if t.resource != Resource.DESERT)

