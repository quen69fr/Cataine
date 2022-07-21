from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from rendering_constants import *
from rendering_functions import alpha_image, render_road
from resource_hand_count import ResourceHandCount, ORDER_RESOURCES
from resource_manager import ResourceManager
from construction import Construction, ConstructionKind
from actions import Action, ActionBuildRoad, ActionBuildColony, ActionBuildTown, ActionBuyDevCard
from player import Player, PlayerManager
from exchange import Exchange
from game_states import GameState, GamePlayingState, GamePlacingColoniesState

if TYPE_CHECKING:
    from render_game import RenderGame


class ManualPlayer(PlayerManager):
    def __init__(self, player: Player):
        PlayerManager.__init__(self, player)
        self.selected_cards: list[int] = []  # TODO
        self.last_hand_cards: ResourceHandCount = ResourceHandCount()  # TODO
        self.render_game: RenderGame | None = None

        self.ongoing_construction: ConstructionKind | None = None
        self.ongoing_exchange: Exchange | None = None
        self.ongoing_bank_exchange: Exchange | None = None

        self.clic = False

    def play(self):
        if not self.clic or self.render_game is None:
            return False

        # Ongoing construction
        action = self.action_ongoing_construction()
        if action is not None and action.available():
            action.apply()
            self.ongoing_construction = None

        self.play_player_buttons()

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

    def play_player_buttons(self):
        i = self.render_game.clic_on_main_player_buttons()
        if i is not None:
            if i == 0:
                self.construction_button()
            else:
                pass  # TODO
        return self.render_game.clic_on_action_button()

    def construction_button(self):
        if self.ongoing_construction is None:
            cost = self.get_selected_resource_cards()
            if cost == ActionBuildRoad.cost:
                self.ongoing_construction = ConstructionKind.ROAD
            elif cost == ActionBuildColony.cost:
                self.ongoing_construction = ConstructionKind.COLONY
            elif cost == ActionBuildTown.cost:
                self.ongoing_construction = ConstructionKind.TOWN
            elif cost == ActionBuyDevCard.cost:
                pass  # TODO
        else:
            self.ongoing_construction = None

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
        if player is None or sum(player.resource_cards.values()) == 0:
            return False
        self.player.steal_card(player)
        return True

    def accept_exchange(self):
        # ----------- TEMP -----------
        self.player.reject_exchange()
        return True
        # ----------- TEMP -----------
        if not self.clic or self.render_game is None:
            return False
        return True  # TODO

    def throw_dice(self):
        if not self.clic or self.render_game is None:
            return False
        return self.render_game.clic_on_action_button()

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
            while old_selected_cards and old_selected_cards[0] < n + self.last_hand_cards[res]:
                num = old_selected_cards.pop(0)
                if num_cards_to_remove > 0:
                    num_cards_to_remove -= 1
                else:
                    self.selected_cards.append(num - n + n2)
            n += self.last_hand_cards[res]
            n2 += self.player.resource_cards[res]
            if self.last_hand_cards[res] < self.player.resource_cards[res]:
                for i in range(self.last_hand_cards[res] - self.player.resource_cards[res], 0):
                    self.selected_cards.append(n2 + i)
        self.last_hand_cards = self.player.resource_cards.copy()

    def update_rendering(self):
        self.update_selected_cards()
        if self.clic and self.render_game is not None:
            x, y = position_hand_resource_cards()
            index_card = self.render_game.clic_cards(sum(self.player.resource_cards.values()), x, y,
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
            if game_sub_state == GamePlayingState.NEXT_TURN:
                if self.ongoing_construction is not None:
                    if self.ongoing_construction == ConstructionKind.ROAD:
                        self.render_build_road(screen)
                    elif self.ongoing_construction == ConstructionKind.COLONY:
                        self.render_build_colony(screen)
                    elif self.ongoing_construction == ConstructionKind.TOWN:
                        self.render_build_town(screen)
            elif game_sub_state == GamePlayingState.MOVE_THIEF:
                self.render_move_thief(screen)

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
