from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from copy import deepcopy

from board import Board
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath
from exchange import Exchange
from resource_hand_count import ResourceHandCount

if TYPE_CHECKING:
    from player import Player


class Strategy:
    exchange_with_others: bool = False

    def __init__(self, board: Board, player: Player):
        self.board = board
        self.player = player

    def change_of_player_and_board(self, board: Board, player: Player):
        self.board = board
        self.player = player

    @abstractmethod
    def play(self) -> bool:
        pass

    @abstractmethod
    def place_initial_colony(self) -> TileIntersection:
        pass

    @abstractmethod
    def place_road_around_initial_colony(self) -> TilePath:
        pass

    @abstractmethod
    def remove_cards_thief(self, num_cards_kept: int) -> ResourceHandCount:
        pass

    @abstractmethod
    def move_thief(self) -> Tile:
        pass

    @abstractmethod
    def steal_card(self) -> Player:
        pass

    @abstractmethod
    def accept_exchange(self, exchange: Exchange) -> bool:
        pass
