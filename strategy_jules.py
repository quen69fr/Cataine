from __future__ import annotations

from typing import TYPE_CHECKING

from strategy import Strategy
from board import Board
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath
from exchange import Exchange
from resource_hand_count import ResourceHandCount

if TYPE_CHECKING:
    from player import Player


class StrategyWithObjectives(Strategy):
    def __init__(self, board: Board, player: Player):
        Strategy.__init__(self, board, player)

    def play(self) -> bool:
        # Can apply any Action
        pass

    def place_initial_colony(self) -> TileIntersection:
        pass

    def place_road_around_initial_colony(self) -> TilePath:
        pass

    def remove_cards_thief(self, num_cards_kept: int) -> ResourceHandCount:
        pass

    def move_thief(self) -> Tile:
        pass

    def steal_card(self) -> Player:
        pass

    def accept_exchange(self, exchange: Exchange) -> bool:
        pass
