from __future__ import annotations

import random

from logs import log
from constants import NUM_VICTORY_POINTS_FOR_VICTORY
from dev_cards import DevCard
from resource import BOARD_LAYOUT_DICE_NUMBERS, BOARD_LAYOUT_RESOURCES, BOARD_PORT_RESOURCES
from board import Board
from color import COLORS_ORDER
from construction import ConstructionKind
from player import Player, PlayerManager
from exchange import BANK_PLAYER_FOR_EXCHANGE
from game_states import GameState, GamePlayingState, GamePlacingColoniesState


class Game:
    board: Board
    players: list[Player]

    def __init__(self, nicknames: list[str]):
        self.board = Board(BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS, BOARD_PORT_RESOURCES)
        self.players = [
            Player(nickname, COLORS_ORDER[i], self.board) for i, nickname in enumerate(nicknames)
        ]
        self.turn_number = 0

        self.dices = (0, 0)

        self.game_state = GameState.PLACING_COLONIES
        self.game_sub_state: GamePlayingState | GamePlacingColoniesState = GamePlacingColoniesState.PLACING_COLONY

    def play(self, player_managers: dict[Player, PlayerManager]):
        if self.game_state == GameState.END:
            return
        current_player = self.get_current_player()
        if self.game_state == GameState.PLACING_COLONIES:
            if self.game_sub_state == GamePlacingColoniesState.PLACING_COLONY:
                if player_managers[current_player].place_initial_colony():
                    self.game_sub_state = GamePlacingColoniesState.PLACING_ROAD
            else:  # self.game_sub_state == GamePlacingColoniesState.PLACING_ROAD:
                if player_managers[current_player].place_initial_road():
                    self.turn_number += 1
                    self.game_sub_state = GamePlacingColoniesState.PLACING_COLONY
                    if self.turn_number == 2 * len(self.players):
                        self.game_state = GameState.PLAYING
                        self.game_sub_state = GamePlayingState.THROW_DICES
        else:
            if self.game_sub_state == GamePlayingState.THROW_DICES:
                if not self._knight_before_playing(player_managers):
                    if player_managers[current_player].throw_dice():
                        self.throw_dice()
                        if sum(self.dices) == 7:
                            for player in self.players:
                                player.move_thief_match_num_cards()
                            if sum(player.num_cards_to_remove_for_thief for player in self.players) == 0:
                                self.game_sub_state = GamePlayingState.MOVE_THIEF
                            else:
                                self.game_sub_state = GamePlayingState.REMOVE_CARDS_THIEF
                        else:
                            self.game_sub_state = GamePlayingState.GET_RESOURCES
            elif self.game_sub_state == GamePlayingState.GET_RESOURCES:
                if player_managers[current_player].get_resources():
                    self.get_resources()
                    self.game_sub_state = GamePlayingState.NEXT_TURN
            elif self.game_sub_state == GamePlayingState.NEXT_TURN:
                self._play_next_turn_state(player_managers)
            elif self.game_sub_state == GamePlayingState.REMOVE_CARDS_THIEF:
                for player in self.players:
                    if player.num_cards_to_remove_for_thief > 0:
                        player_managers[player].remove_cards_for_thief()
                if sum(player.num_cards_to_remove_for_thief for player in self.players) == 0:
                    self.game_sub_state = GamePlayingState.MOVE_THIEF
            elif self.game_sub_state == GamePlayingState.MOVE_THIEF:
                if player_managers[current_player].move_thief():
                    if current_player.can_steal():
                        self.game_sub_state = GamePlayingState.STEAL_CARD
                    else:
                        self.game_sub_state = GamePlayingState.NEXT_TURN
            else:  # self.game_sub_state == GamePlayingState.STEAL_CARD:
                if player_managers[current_player].steal_card():
                    self.game_sub_state = GamePlayingState.NEXT_TURN

    def _knight_before_playing(self, player_managers: dict[Player, PlayerManager]):
        current_player = self.get_current_player()
        if current_player.dev_card_in_action is not None:
            if current_player.dev_card_in_action == DevCard.KNIGHT:
                if player_managers[current_player].move_thief():
                    if current_player.can_steal():
                        current_player.dev_card_in_action = DevCard.KNIGHT_STEAL_CARD
                    else:
                        current_player.dev_card_in_action = None
            else:  # current_player.dev_card_in_action == DevCard.KNIGHT_STEAL_CARD
                if player_managers[current_player].steal_card():
                    current_player.dev_card_in_action = None
            return True
        return False

    def _play_next_turn_state(self, player_managers: dict[Player, PlayerManager]):
        current_player = self.get_current_player()

        # Is there already proposed exchanges ? And maybe answers ?
        new_proposal = True
        for player in self.get_non_current_players():
            if player.exchange_asked is not None:
                player_managers[player].accept_exchange()
                if player.exchange_accepted:
                    player.exchange_asked.apply(player, current_player)
                    current_player.exchanges = None
                    for p in self.get_non_current_players():
                        p.exchange_asked_done()
                    return
                if player.exchange_asked is not None:
                    new_proposal = False

        if not new_proposal:
            return

        # Is there exchanges to propose ?
        if current_player.exchanges:
            exchange = current_player.exchanges.pop(0)
            if current_player.can_exchange_with_the_bank(exchange):
                exchange.apply(current_player, BANK_PLAYER_FOR_EXCHANGE)
                current_player.exchanges = None
                return
            else:
                for player in self.get_non_current_players():
                    player.ask_for_exchange(exchange.inverse())
                return

        # A dev card has been revealed ?
        if current_player.dev_card_in_action is not None:
            if current_player.dev_card_in_action == DevCard.KNIGHT:
                if player_managers[current_player].move_thief():
                    if current_player.can_steal():
                        current_player.dev_card_in_action = DevCard.KNIGHT_STEAL_CARD
                    else:
                        current_player.dev_card_in_action = None
            elif current_player.dev_card_in_action == DevCard.KNIGHT_STEAL_CARD:
                if player_managers[current_player].steal_card():
                    current_player.dev_card_in_action = None
            elif current_player.dev_card_in_action == DevCard.FREE_CARDS:
                if player_managers[current_player].free_card():
                    current_player.dev_card_in_action = DevCard.FREE_CARDS_ONE_CARD_LASTING
            elif current_player.dev_card_in_action == DevCard.FREE_CARDS_ONE_CARD_LASTING:
                if player_managers[current_player].free_card():
                    current_player.dev_card_in_action = None
            elif current_player.dev_card_in_action == DevCard.FREE_ROADS:
                if player_managers[current_player].place_free_road():
                    current_player.dev_card_in_action = DevCard.FREE_ROADS_ONE_ROAD_LASTING
            elif current_player.dev_card_in_action == DevCard.FREE_ROADS_ONE_ROAD_LASTING:
                if player_managers[current_player].place_free_road():
                    current_player.dev_card_in_action = None
            elif current_player.dev_card_in_action == DevCard.MONOPOLY:
                if player_managers[current_player].monopoly():
                    res = current_player.monopoly_resource
                    assert res is not None
                    for player in self.get_non_current_players():
                        current_player.add_one_resource(res, player.resource_cards[res])
                        player.resource_cards[res] = 0
                    current_player.monopoly_resource = None
                    current_player.dev_card_in_action = None
            else:
                current_player.dev_card_in_action = None
            return

        # Then the current player can play
        if player_managers[current_player].play():
            current_player.exchanges = None
            current_player.end_turn()
            if current_player.num_victory_points() >= NUM_VICTORY_POINTS_FOR_VICTORY:
                self.game_state = GameState.END
            else:
                self.game_sub_state = GamePlayingState.THROW_DICES
                self.turn_number += 1

    def throw_dice(self):
        log(f"\nPlayer turn: {self.get_current_player()}")
        self.dices = (random.randint(1, 6), random.randint(1, 6))

    def get_resources(self):
        r = sum(self.dices)
        assert not r == 7
        # Give resources to players
        for tile in self.board.tiles:
            if tile.dice_number == r and not tile == self.board.thief_tile:
                for inte in tile.intersections:
                    if inte.content is None:
                        continue
                    inte.content.player.add_one_resource(tile.resource)
                    if inte.content.kind == ConstructionKind.TOWN:
                        inte.content.player.add_one_resource(tile.resource)

    def get_current_player(self) -> Player:
        if self.game_state == GameState.PLACING_COLONIES:
            if self.turn_number < len(self.players):
                return self.players[self.turn_number]
            return self.players[2 * len(self.players) - self.turn_number - 1]
        return self.players[self.turn_number % len(self.players)]

    def get_non_current_players(self) -> list[Player]:
        index = self.turn_number % len(self.players)
        return self.players[:index] + self.players[index + 1:]

    def get_players_except_one(self, player: Player) -> list[Player]:
        index = self.players.index(player)
        return self.players[:index] + self.players[index + 1:]
