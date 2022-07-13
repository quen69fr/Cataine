from __future__ import annotations

import random
from enum import Enum
from resource import (BOARD_LAYOUT_DICE_NUMBERS, BOARD_LAYOUT_RESOURCES,
                      BOARD_PORT_RESOURCES)

import pygments

from board import Board
from color import Color
from construction import ConstructionKind
from player import Player
from tile import Tile


class GameState(Enum):
    PLACING_COLONIES = 1
    PLAYING = 2

class Game:
    board: Board
    players: list[Player]

    def __init__(self):
        self.board = Board(BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS, BOARD_PORT_RESOURCES)
        self.players = [
            Player(Color.RED, self.board),
            Player(Color.BLUE, self.board)
        ]
        self.turn_number = 0

        self.game_state = GameState.PLACING_COLONIES

    def turn(self):
        if self.game_state == GameState.PLACING_COLONIES:
            self._turn_placing_colonies()
            if self.turn_number == len(self.players) * 2 - 1:
                self.game_state = GameState.PLAYING
        else:
            self._turn_playing()
        self.turn_number += 1

    def _give_resources_to_players(self, tile: Tile):
        for inte in tile.intersections:
            if inte.content is None:
                continue

            if inte.content.kind == ConstructionKind.COLONY:
                inte.content.player.add_resource_card(tile.resource)
            elif inte.content.kind == ConstructionKind.TOWN:
                inte.content.player.add_resource_card(tile.resource)
                inte.content.player.add_resource_card(tile.resource)



    def _turn_playing(self):
        r = random.randint(1, 6) + random.randint(1, 6)
        print("dice result", r)
        if r == 7:
            # check number of cards
            pass # TODO
        else:
            for t in self.board.tiles:
                if t.dice_number == r:
                    self._give_resources_to_players(t)

        self.players[self.turn_number % len(self.players)].play()

    def _turn_placing_colonies(self):
        self.players[self.turn_number % len(self.players)].place_initial_colony()

    def render(self, screen: pygments.Surface):
        self.board.render(40, 40, screen)
