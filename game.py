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
from rendering_functions import render_text
from tile import Tile


class GameState(Enum):
    PLACING_COLONIES = 1
    PLAYING = 2
    END = 3


class GamePlayingState(Enum):
    THROW_DICES = 0
    GET_RESOURCES = 1
    NEXT_TURN = 2
    MOVE_THIEF = 3
    STEAL_CARD = 4


class GamePlacingColoniesState(Enum):
    PLACING_COLONY = 0
    PLACING_ROAD = 1


class Game:
    board: Board
    players: list[Player]

    def __init__(self):
        self.board = Board(BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS, BOARD_PORT_RESOURCES)
        self.players = [
            Player("Mathieu", Color.WHITE, self.board),
            Player("Quentin", Color.RED, self.board),
            Player("Juliette", Color.BLUE, self.board),
            Player("Sarah", Color.ORANGE, self.board),
        ]
        self.turn_number = 0

        self.dices = (0, 0)

        self.game_state = GameState.PLACING_COLONIES
        self.game_sub_state: GamePlayingState | GamePlacingColoniesState = GamePlacingColoniesState.PLACING_COLONY

    def next_turn_step_ia(self):
        if self.game_state == GameState.PLACING_COLONIES:
            if self.game_sub_state == GamePlacingColoniesState.PLACING_COLONY:
                self.place_initial_colony()
                self.game_sub_state = GamePlacingColoniesState.PLACING_ROAD
            else:  # self.game_sub_state == GamePlacingColoniesState.PLACING_ROAD:
                self.place_initial_road()
                self.end_placing_turn()
        else:
            if self.game_sub_state == GamePlayingState.THROW_DICES:
                self.throw_dice()
            elif self.game_sub_state == GamePlayingState.GET_RESOURCES:
                self.get_resources()
            elif self.game_sub_state == GamePlayingState.NEXT_TURN:
                self.ia_player_plays()
                self.end_playing_turn()
            elif self.game_sub_state == GamePlayingState.MOVE_THIEF:
                self.move_thief()
            else:  # self.game_sub_state == GamePlayingState.STEAL_CARD:
                self.steal_card_thief()

    def complete_turn_ai(self):
        t = self.turn_number
        while self.turn_number == t:
            self.next_turn_step_ia()

    def place_initial_colony(self):
        self.get_current_player().place_initial_colony(self.turn_number >= len(self.players))

    def place_initial_road(self):
        self.get_current_player().place_initial_road()

    def end_placing_turn(self):
        self.turn_number += 1
        self.game_sub_state = GamePlacingColoniesState.PLACING_COLONY
        if self.turn_number == 2 * len(self.players):
            self.game_state = GameState.PLAYING
            self.game_sub_state = GamePlayingState.THROW_DICES

    def throw_dice(self):
        self.dices = (random.randint(1, 6), random.randint(1, 6))
        if sum(self.dices) == 7:
            self.game_sub_state = GamePlayingState.MOVE_THIEF
        else:
            self.game_sub_state = GamePlayingState.GET_RESOURCES

    def get_resources(self):
        r = sum(self.dices)
        assert not r == 7
        for t in self.board.tiles:
            if t.dice_number == r:
                self._give_resources_to_players(t)
        self.game_sub_state = GamePlayingState.NEXT_TURN

    def move_thief(self):
        current_player = self.get_current_player()
        current_player.move_thief()
        if current_player.can_steal():
            self.game_sub_state = GamePlayingState.STEAL_CARD
        else:
            self.game_sub_state = GamePlayingState.NEXT_TURN

    def steal_card_thief(self):
        self.get_current_player().steal_card()
        self.game_sub_state = GamePlayingState.NEXT_TURN

    def ia_player_plays(self):
        self.get_current_player().play(self.get_non_current_players())

    def end_playing_turn(self):
        self.game_sub_state = GamePlayingState.THROW_DICES
        self.turn_number += 1

    def _give_resources_to_players(self, tile: Tile):
        for inte in tile.intersections:
            if inte.content is None:
                continue
            inte.content.player.resource_cards.add_one(tile.resource)
            if inte.content.kind == ConstructionKind.TOWN:
                inte.content.player.resource_cards.add_one(tile.resource)

    def get_current_player(self) -> Player:
        if self.game_state == GameState.PLACING_COLONIES:
            if self.turn_number < len(self.players):
                return self.players[self.turn_number]
            return self.players[2 * len(self.players) - self.turn_number - 1]
        return self.players[self.turn_number % len(self.players)]

    def get_non_current_players(self) -> list[Player]:
        index = self.turn_number % len(self.players)
        return self.players[:index] + self.players[index + 1:]

    def _turn_placing_colonies(self):
        self.get_current_player().place_initial_colony(self.turn_number >= len(self.players))

    def render(self, screen: pygame.Surface):
        self.board.render(40, 40, screen)
        for i, player in enumerate(self.players):
            player.render_draft(screen, 800 + 250 * (i // 2), 50 + 300 * (i % 2), self.get_current_player() == player)

        render_text(screen, f"turn number: {self.turn_number}", 0, 0, 20, (0, 0, 0), False, None)
