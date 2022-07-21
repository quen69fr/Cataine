from __future__ import annotations

import pygame

from rendering_constants import WIDTH_PLAYER_SIDE, X_BOARD, Y_BOARD
from rendering_functions import alpha_image, render_road
from resource_manager import ResourceManager
from construction import ConstructionKind
from actions import Action
from player import Player, PlayerManager
from exchange import Exchange
from game_states import GameState, GamePlayingState, GamePlacingColoniesState


class ManualPlayer(PlayerManager):
    def __init__(self, player: Player):
        PlayerManager.__init__(self, player)
        self.non_selected_cards = []  # TODO
        self.cards = []  # TODO

        self.ongoing_action: Action | None = None

        self.clic = False

    def play(self):
        # TODO
        if not self.clic:
            return False
        return True  # TODO

    def place_initial_colony(self):
        if not self.clic:
            return False
        x, y = pygame.mouse.get_pos()
        inter = self.player.board.mouse_on_intersection(X_BOARD, Y_BOARD, x, y)
        if inter is not None and inter.can_build():
            self.player.place_initial_colony(inter)
            return True
        return False

    def place_initial_road(self):
        if not self.clic:
            return False
        x, y = pygame.mouse.get_pos()
        path = self.player.board.mouse_on_path(X_BOARD, Y_BOARD, x, y)
        if path is not None and path.road_player is None:
            for inter in path.intersections:
                possible = True
                for p in inter.neighbour_paths:
                    if p.road_player is not None:
                        possible = False
                        break
                if possible:
                    self.player.place_initial_road(path)
                    return True
        return False

    def remove_cards_for_thief(self):
        if not self.clic:
            return False
        return True  # TODO

    def move_thief(self):
        if not self.clic:
            return False
        return True  # TODO

    def steal_card(self):
        if not self.clic:
            return False
        return True  # TODO

    def accept_exchange(self):
        if not self.clic:
            return False
        return True  # TODO

    def throw_dice(self):
        if not self.clic:
            return False
        return True  # TODO

    def get_resources(self):
        if not self.clic:
            return False
        return True  # TODO

    def render_my_turn(self, screen: pygame.Surface, game_state: GameState,
                       game_sub_state: GamePlayingState | GamePlacingColoniesState):
        if game_state == GameState.PLACING_COLONIES:
            if game_sub_state == GamePlacingColoniesState.PLACING_COLONY:
                self.render_build_colony(screen)
            else:
                self.render_build_road(screen)
        elif game_sub_state == GameState.PLAYING:
            pass  # TODO

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
