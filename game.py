from __future__ import annotations

import random
from enum import Enum
from resource import (BOARD_LAYOUT_DICE_NUMBERS, BOARD_LAYOUT_RESOURCES,
                      BOARD_PORT_RESOURCES)

import pygame

from board import Board
from color import Color
from construction import ConstructionKind
from player import Player
from render_text import render_text
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
            Player(Color.BLUE, self.board),
            Player(Color.ORANGE, self.board)
        ]
        self.turn_number = 0
        self.halfturn_flag = True

        self.game_state = GameState.PLACING_COLONIES

    def turn(self):
        if self.game_state == GameState.PLACING_COLONIES:
            self._turn_placing_colonies()
            if self.turn_number == len(self.players) * 2 - 1:
                self.game_state = GameState.PLAYING
        else:
            self._throw_dice()
            self._current_player_plays()
        self.turn_number += 1

    def halfturn(self):
        if self.game_state == GameState.PLACING_COLONIES:
            print("\nPlayer:", self.get_current_player())
            self.turn()
            return

        if self.halfturn_flag:
            print("\nPlayer:", self.get_current_player())
            self._throw_dice()
        else:
            self._current_player_plays()
            self.turn_number += 1
        self.halfturn_flag = not self.halfturn_flag

    def _give_resources_to_players(self, tile: Tile):
        for inte in tile.intersections:
            if inte.content is None:
                continue

            if inte.content.kind == ConstructionKind.COLONY:
                # print(f"{inte.content.player} receives 1 {tile.resource}")
                inte.content.player.resource_cards.add_one(tile.resource)
            elif inte.content.kind == ConstructionKind.TOWN:
                inte.content.player.resource_cards.add_one(tile.resource)
                inte.content.player.resource_cards.add_one(tile.resource)
                # print(f"{inte.content.player} receives 2 {tile.resource}")

    def _throw_dice(self):
        r = random.randint(1, 6) + random.randint(1, 6)
        print("Dice result:", r)
        if r == 7:
            # check number of cards
            pass  # TODO
        else:
            for t in self.board.tiles:
                if t.dice_number == r:
                    self._give_resources_to_players(t)

    def get_current_player(self) -> Player:
        return self.players[self.turn_number % len(self.players)]

    def get_non_current_players(self) -> list[Player]:
        index = self.turn_number % len(self.players)
        return self.players[:index] + self.players[index + 1:]

    def _current_player_plays(self):
        self.get_current_player().play(self.get_non_current_players())

    def _turn_placing_colonies(self):
        self.get_current_player().place_initial_colony()

    def render(self, screen: pygame.Surface):
        self.board.render(40, 40, screen)
        for i, player in enumerate(self.players):
            player.render(screen, 800 + 250 * (i // 2), 50 + 300 * (i % 2), self.turn_number % len(self.players) == i)

        render_text(screen, f"turn number: {self.turn_number}", 0, 0, 20, 0, False, None)
