from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from resource import Resource
from dev_cards import DevCard
from rendering_constants import *
from rendering_functions import alpha_image, render_road
from resource_hand_count import ResourceHandCount, ORDER_RESOURCES
from resource_manager import ResourceManager
from construction import Construction, ConstructionKind
from actions import Action, ActionBuildRoad, ActionBuildColony, ActionBuildTown, ActionBuyDevCard, ActionRevealDevCard
from player import Player, PlayerManager
from exchange import Exchange, BANK_PLAYER_FOR_EXCHANGE
from game_states import GameState, GamePlayingState, GamePlacingColoniesState

if TYPE_CHECKING:
    from render_game import RenderGame


class ManualPlayer(PlayerManager):
    def __init__(self, player: Player, auto_refuse_ratio_max_exchange: float = 0):
        PlayerManager.__init__(self, player)
        self.selected_cards: list[int] = []
        self.last_hand_cards: ResourceHandCount = ResourceHandCount()
        self.render_game: RenderGame | None = None

        self.ongoing_construction: ConstructionKind | None = None
        self.ongoing_exchange: Exchange | None = None
        self.ongoing_bank_exchange: Exchange | None = None

        self.refuse_ratio_max_exchange = auto_refuse_ratio_max_exchange
        self.clic = False

    def play(self):
        if not self.clic or self.render_game is None:
            return False

        if self.ongoing_construction is not None:
            action = self.action_ongoing_construction()
            if action is not None and action.available():
                action.apply()
                self.ongoing_construction = None
            elif self.render_game.clic_on_main_player_buttons() == 0:
                self.ongoing_construction = None
            return False
        if self.ongoing_bank_exchange is not None:
            x, y = position_bank_resource_exchange()
            res = self.render_game.clic_on_bank_resource(x, y)
            if res is not None:
                self.ongoing_bank_exchange.gain.add_one(res)
                self.ongoing_bank_exchange.apply(self.player, BANK_PLAYER_FOR_EXCHANGE)
                self.ongoing_bank_exchange = None
            elif self.render_game.clic_on_main_player_buttons() == 1:
                self.ongoing_bank_exchange = None
            return False
        if self.ongoing_exchange is not None:
            if self.play_ongoing_exchanges():
                self.player.propose_exchanges([self.ongoing_exchange])
                self.ongoing_exchange = None
            elif self.render_game.clic_on_main_player_buttons() == 2:
                self.ongoing_exchange = None
            return False

        x, y = position_hand_dev_cards()
        index_card = self.render_game.clic_cards(len(self.player.dev_cards), x, y, ANGLE_MAX_CARDS_DEV_AND_EXCHANGE)
        if index_card is not None:
            action = ActionRevealDevCard(self.player.dev_cards[index_card], self.player)
            if action.available():
                action.apply()
            return False

        num_button = self.render_game.clic_on_main_player_buttons()
        if num_button is not None:
            if num_button == 0:
                self.construction_button()
            elif num_button == 1:
                self.bank_button()
            else:
                self.exchange_button()
            return False

        return self.render_game.clic_on_action_button()

    def action_ongoing_construction(self) -> Action | None:
        x, y = pygame.mouse.get_pos()
        if self.ongoing_construction == ConstructionKind.COLONY or self.ongoing_construction == ConstructionKind.TOWN:
            inter = self.player.board.mouse_on_intersection(X_BOARD, Y_BOARD, x, y)
            if inter is None:
                return None
            if self.ongoing_construction == ConstructionKind.COLONY:
                return ActionBuildColony(inter, self.player)
            else:
                return ActionBuildTown(inter, self.player)
        elif self.ongoing_construction == ConstructionKind.ROAD:
            path = self.player.board.mouse_on_path(X_BOARD, Y_BOARD, x, y)
            if path is None:
                return None
            return ActionBuildRoad(path, self.player)
        return None

    def play_ongoing_exchanges(self):
        assert self.ongoing_exchange is not None
        x, y = position_resources_exchange_box()
        res = self.render_game.clic_on_bank_resource(x, y)
        if res is not None:
            self.ongoing_exchange.gain.add_one(res)
        i = self.render_game.clic_on_exchange_button()
        if i is None:
            return False
        if i == 0:
            self.ongoing_exchange = None
            return False
        if not sum(self.ongoing_exchange.gain.values()) > 0:
            return False
        return True

    def construction_button(self):
        cost = self.get_selected_resource_cards()
        if cost == ActionBuildRoad.cost:
            self.ongoing_construction = ConstructionKind.ROAD
        elif cost == ActionBuildColony.cost:
            self.ongoing_construction = ConstructionKind.COLONY
        elif cost == ActionBuildTown.cost:
            self.ongoing_construction = ConstructionKind.TOWN
        elif cost == ActionBuyDevCard.cost:
            ActionBuyDevCard(self.player).apply()

    def bank_button(self):
        if len(self.selected_cards) < 2 or len(self.selected_cards) > 4:
            return

        list_cards = list(self.player.resource_cards.list_resources())
        res = list_cards[self.selected_cards[0]]
        for i in self.selected_cards:
            if not res == list_cards[i]:
                return

        ports = self.player.get_ports()
        if len(self.selected_cards) == 2 and res not in ports:
            return
        if Resource.P_3_FOR_1 in ports:
            if len(self.selected_cards) == 4:
                return
        else:
            if len(self.selected_cards) == 3:
                return

        self.ongoing_bank_exchange = Exchange(ResourceHandCount(), self.get_selected_resource_cards())

    def exchange_button(self):
        if len(self.selected_cards) == 0:
            return
        self.ongoing_exchange = Exchange(ResourceHandCount(), self.get_selected_resource_cards())

    def place_initial_colony(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = pygame.mouse.get_pos()
        inter = self.player.board.mouse_on_intersection(X_BOARD, Y_BOARD, x, y)
        if inter is not None and inter.can_build():
            self.player.place_initial_colony(inter)
            return True
        return False

    def place_initial_road(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = pygame.mouse.get_pos()
        path = self.player.board.mouse_on_path(X_BOARD, Y_BOARD, x, y)
        if path is not None and path.road_player is None:
            for inter in path.intersections:
                if inter.content == Construction(ConstructionKind.COLONY, self.player):
                    for p in inter.neighbour_paths:
                        if p.road_player is not None:
                            return False
                    self.player.place_initial_road(path)
                    return True
        return False

    def remove_cards_for_thief(self):
        if not self.clic or self.render_game is None:
            return False
        if len(self.selected_cards) == self.player.num_cards_to_remove_for_thief \
                and self.render_game.clic_on_action_button():
            new_resources = self.player.resource_cards.copy()
            list_cards = list(self.player.resource_cards.list_resources())
            for i in self.selected_cards:
                new_resources.try_consume_one(list_cards[i])
            self.player.remove_cards_for_thief(new_resources)
            return True
        return False

    def move_thief(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = pygame.mouse.get_pos()
        tile = self.player.board.mouse_on_tile(X_BOARD, Y_BOARD, x, y)
        if tile is None or tile == self.player.board.thief_tile:
            return False
        self.player.move_thief(tile)
        return True

    def steal_card(self):
        if not self.clic or self.render_game is None:
            return False
        player = self.render_game.clic_on_secondary_players()
        if player is None:
            return False
        if not self.player.can_steal_player(player):
            return False
        self.player.steal_card(player)
        return True

    def accept_exchange(self):
        if self.player.exchange_asked.ratio() < self.refuse_ratio_max_exchange:
            self.player.reject_exchange()
            return True
        if not self.clic or self.render_game is None:
            return False
        i = self.render_game.clic_on_exchange_button()
        if i is None:
            return False
        if i == 0:
            self.player.reject_exchange()
        else:
            self.player.accept_exchange()
        return True

    def throw_dice(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = position_hand_dev_cards()
        index_card = self.render_game.clic_cards(len(self.player.dev_cards), x, y, ANGLE_MAX_CARDS_DEV_AND_EXCHANGE)
        if index_card is not None:
            action = ActionRevealDevCard(self.player.dev_cards[index_card], self.player)
            if action.available(before_play=True):
                action.apply()
            return False
        return self.render_game.clic_on_action_button()

    def place_free_road(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = pygame.mouse.get_pos()
        path = self.player.board.mouse_on_path(X_BOARD, Y_BOARD, x, y)
        if path is None:
            return False
        action = ActionBuildRoad(path, self.player)
        if not action.available():
            return False
        # action.apply()
        self.player.add_road(path)
        return True

    def free_card(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = position_bank_resource_exchange()
        res = self.render_game.clic_on_bank_resource(x, y)
        if res is None:
            return False
        self.player.add_one_resource(res)
        return True

    def monopoly(self):
        if not self.clic or self.render_game is None:
            return False
        x, y = position_bank_monopoly()
        res = self.render_game.clic_on_bank_resource(x, y)
        if res is None:
            return False
        self.player.monopoly(res)
        return True

    def get_resources(self):
        if not self.clic or self.render_game is None:
            return False
        return self.render_game.clic_on_action_button()

    def get_selected_resource_cards(self) -> ResourceHandCount:
        selected_resources = ResourceHandCount()
        cards = list(self.player.resource_cards.list_resources())
        for i in self.selected_cards:
            selected_resources.add_one(cards[i])
        return selected_resources

    def update_selected_cards(self):
        if self.last_hand_cards == self.player.resource_cards:
            return
        old_selected_cards = self.selected_cards.copy()
        self.selected_cards = []
        n = 0
        n2 = 0
        for res in ORDER_RESOURCES:
            num_cards_to_remove = max(0, self.last_hand_cards[res] - self.player.resource_cards[res])
            shift = 0
            while old_selected_cards and old_selected_cards[0] < n + self.last_hand_cards[res]:
                num = old_selected_cards.pop(0)
                if num - n - shift < self.player.resource_cards[res]:
                    if num_cards_to_remove > 0:
                        num_cards_to_remove -= 1
                        shift += 1
                    else:
                        self.selected_cards.append(num - shift - n + n2)
            n += self.last_hand_cards[res]
            n2 += self.player.resource_cards[res]
            if self.last_hand_cards[res] < self.player.resource_cards[res]:
                for i in range(self.last_hand_cards[res] - self.player.resource_cards[res], 0):
                    self.selected_cards.append(n2 + i)
        self.last_hand_cards = self.player.resource_cards.copy()

    def update_rendering(self):
        self.update_selected_cards()
        if not self.clic or self.render_game is None:
            return
        if self.ongoing_construction is None \
                and self.ongoing_bank_exchange is None \
                and self.ongoing_exchange is None:
            x, y = position_hand_resource_cards()
            index_card = self.render_game.clic_cards(self.player.num_resources(), x, y,
                                                     ANGLE_MAX_CARDS_RESOURCE)
            if index_card is not None:
                if index_card in self.selected_cards:
                    self.selected_cards.remove(index_card)
                else:
                    self.add_selected_card(index_card)

    def add_selected_card(self, index_card: int):
        i = 0
        while i < len(self.selected_cards) and self.selected_cards[i] < index_card:
            i += 1
        self.selected_cards.insert(i, index_card)

    def render_my_turn(self, screen: pygame.Surface, game_state: GameState,
                       game_sub_state: GamePlayingState | GamePlacingColoniesState):
        if game_state == GameState.PLACING_COLONIES:
            if game_sub_state == GamePlacingColoniesState.PLACING_COLONY:
                self.render_build_colony(screen)
            else:
                self.render_build_road(screen)
        elif game_state == GameState.PLAYING:
            if game_sub_state == GamePlayingState.THROW_DICES:
                if self.player.dev_card_in_action is not None:
                    if self.player.dev_card_in_action == DevCard.KNIGHT:
                        self.render_move_thief(screen)
                    elif self.player.dev_card_in_action == DevCard.KNIGHT_STEAL_CARD:
                        self.render_steal_card(screen)
            elif game_sub_state == GamePlayingState.NEXT_TURN:
                if self.ongoing_construction is not None:
                    if self.ongoing_construction == ConstructionKind.ROAD:
                        self.render_build_road(screen)
                    elif self.ongoing_construction == ConstructionKind.COLONY:
                        self.render_build_colony(screen)
                    elif self.ongoing_construction == ConstructionKind.TOWN:
                        self.render_build_town(screen)
                elif self.player.dev_card_in_action is not None:
                    if self.player.dev_card_in_action == DevCard.KNIGHT:
                        self.render_move_thief(screen)
                    elif self.player.dev_card_in_action == DevCard.KNIGHT_STEAL_CARD:
                        self.render_steal_card(screen)
                    elif self.player.dev_card_in_action == DevCard.FREE_ROADS \
                            or self.player.dev_card_in_action == DevCard.FREE_ROADS_ONE_ROAD_LASTING:
                        self.render_build_road(screen)
            elif game_sub_state == GamePlayingState.MOVE_THIEF:
                self.render_move_thief(screen)
            elif game_sub_state == GamePlayingState.STEAL_CARD:
                self.render_steal_card(screen)

    def render_build_road(self, screen: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        if x > WIDTH_PLAYER_SIDE:
            img = pygame.Surface((2 * ResourceManager.TILE_PATH_LENGTH, 2 * ResourceManager.TILE_PATH_LENGTH),
                                 pygame.SRCALPHA)
            path = self.player.board.mouse_on_path(X_BOARD, Y_BOARD, x, y)
            if path is None:
                p1 = x - (ResourceManager.TILE_PATH_LENGTH + 1) // 2, y
                p2 = x + ResourceManager.TILE_PATH_LENGTH // 2, y
            else:
                p1 = path.intersections[0].position(X_BOARD, Y_BOARD)
                p2 = path.intersections[1].position(X_BOARD, Y_BOARD)
                x, y = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
            x -= ResourceManager.TILE_PATH_LENGTH
            y -= ResourceManager.TILE_PATH_LENGTH
            render_road(img, (p1[0] - x, p1[1] - y), (p2[0] - x, p2[1] - y), ResourceManager.ROAD_WIDTH,
                        self.player.color.value)
            screen.blit(alpha_image(img, 150), (x, y))

    def render_build_colony(self, screen: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        if x > WIDTH_PLAYER_SIDE:
            img = ResourceManager.CONSTRUCTIONS[ConstructionKind.COLONY][self.player.color]
            inter = self.player.board.mouse_on_intersection(X_BOARD, Y_BOARD, x, y)
            if inter is not None:
                x, y = inter.position(X_BOARD, Y_BOARD)
            screen.blit(alpha_image(img, 150), (x - img.get_width() // 2, y - img.get_height() // 2))

    def render_build_town(self, screen: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        if x > WIDTH_PLAYER_SIDE:
            img = ResourceManager.CONSTRUCTIONS[ConstructionKind.TOWN][self.player.color]
            inter = self.player.board.mouse_on_intersection(X_BOARD, Y_BOARD, x, y)
            if inter is not None:
                x, y = inter.position(X_BOARD, Y_BOARD)
            screen.blit(alpha_image(img, 150), (x - img.get_width() // 2, y - img.get_height() // 2))

    def render_move_thief(self, screen: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        if x > WIDTH_PLAYER_SIDE:
            img = ResourceManager.THIEF_IMAGE
            tile = self.player.board.mouse_on_tile(X_BOARD, Y_BOARD, x, y)
            if tile is not None:
                x, y = tile.position(X_BOARD, Y_BOARD)
                x += ResourceManager.TILE_WIDTH // 2
                y += ResourceManager.TILE_HEIGHT // 2
            screen.blit(alpha_image(img, 150), (x - img.get_width() // 2, y - img.get_height() // 2))

    def render_steal_card(self, screen: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        if x < WIDTH_PLAYER_SIDE:
            x_mouse, y_mouse = pygame.mouse.get_pos()
            _, size = y_size_secondary_player()
            for i, (xp, yp) in enumerate(position_secondary_players(len(self.render_game.game.players) - 1)):
                if 0 <= x_mouse - xp <= size and 0 <= y_mouse - yp <= size:
                    x, y = xp + size // 2, yp + size // 2
                    break
            img = ResourceManager.THIEF_IMAGE
            screen.blit(alpha_image(img, 150), (x - img.get_width() // 2, y - img.get_height() // 2))
