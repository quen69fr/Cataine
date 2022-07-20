
import pygame.gfxdraw
from math import cos, sin, pi

from constants import NUM_VICTORY_POINTS_FOR_VICTORY
from game import Game, GameState, GamePlayingState, GamePlacingColoniesState
from color import Color
from player import Player
from dev_cards import DevCard
from resource import Resource
from resource_manager import ResourceManager
from rendering_functions import render_text
from construction import ConstructionKind, NUM_CONSTRUCTION_MAX


WIDTH = 1360
HEIGHT = 700
WIDTH_PLAYER_SIDE = 615
Y_BOARD = 44
MARGINS = 8
HEIGHT_TITLE = 130
HEIGHT_ACTIONS_BOX = 80
Y_BUTTONS_IN_MAIN_PLAYER_BOX = 225
HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX = 40
WIDTH_BUTTON_ACTION = 260
HEIGHT_BUTTON_ACTION = 40
SIZE_DICE = 60


def x_position_after_dice() -> int:
    return MARGINS + HEIGHT_ACTIONS_BOX + (HEIGHT_ACTIONS_BOX + SIZE_DICE) // 2


def position_button_action() -> (int, int):
    return ((x_position_after_dice() + WIDTH_PLAYER_SIDE - WIDTH_BUTTON_ACTION) // 2,
            2 * MARGINS + HEIGHT_TITLE + (HEIGHT_ACTIONS_BOX - HEIGHT_BUTTON_ACTION) // 2)


class RenderGame:
    def __init__(self, game: Game):
        self.game: Game = game
        self.main_player: Player = self.game.players[0]

        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))

    def change_main_player(self):
        self.main_player = self.game.players[(self.game.players.index(self.main_player) + 1) % len(self.game.players)]
    
    def rectangle(self, x: int, y: int, width: int, height: int):
        self.screen.fill((0, 0, 0), (x, y, width, height))
        self.screen.fill((255, 255, 255), (x + 3, y + 3, width - 6, height - 6))

    def button(self, x: int, y: int, width: int, height: int, text: str, size_text: int,
               color_bounds: tuple[int, int, int], color_inside: tuple[int, int, int],
               color_text: tuple[int, int, int] = None):
        self.screen.fill(color_bounds, (x, y, width, height))
        self.screen.fill(color_inside, (x + 3, y + 3, width - 6, height - 6))
        render_text(self.screen, text, x + width // 2, y + height // 2, size_text, color_text)

    def render_card(self, card: Resource | DevCard, x: int, y: int, angle: float, radius: int):
        a_rad = angle * pi / 180
        x_center = x - radius * sin(a_rad)
        y_center = y - radius * cos(a_rad)

        image = pygame.transform.rotozoom(ResourceManager.CARDS_RESOURCES_AND_DEV[card], angle, 1)

        self.screen.blit(image, (int(x_center - image.get_width() / 2), int(y_center - image.get_height() / 2)))

    def render_cards(self, cards: list[Resource | DevCard], x: int, y: int, angle_max: float):
        angle_min = 13
        angle_max = angle_max
        r = 200  # +15 if selected

        num_cards = len(cards)

        da = angle_max / num_cards if num_cards > angle_max / angle_min else angle_min

        for i, card in enumerate(cards):
            a = (num_cards - i - 0.5 - num_cards / 2) * da
            self.render_card(card, x, y, a, r)

    def render_dice(self, x: int, y: int, num: int):
        def render_point(x_, y_):
            pygame.gfxdraw.aacircle(self.screen, x_, y_, 5, (50, 50, 50))
            pygame.gfxdraw.filled_circle(self.screen, x_, y_, 5, (50, 50, 50))

        self.screen.fill((190, 190, 190), (x, y, SIZE_DICE, SIZE_DICE), 0)
        m = 15
        if num == 1 or num == 3 or num == 5:
            render_point(x + SIZE_DICE // 2, y + SIZE_DICE // 2)
        if num > 1:
            render_point(x + SIZE_DICE - m, y + m)
            render_point(x + m, y + SIZE_DICE - m)
        if num >= 4:
            render_point(x + m, y + m)
            render_point(x + SIZE_DICE - m, y + SIZE_DICE - m)
        if num == 6:
            render_point(x + m, y + SIZE_DICE // 2)
            render_point(x + SIZE_DICE - m, y + SIZE_DICE // 2)

    def render(self):
        self.screen.blit(ResourceManager.BACKGROUND, (0, 0))
        self.render_title()
        self.render_actions_box()
        self.render_players()
    
    def render_title(self):
        self.rectangle(MARGINS, MARGINS, WIDTH_PLAYER_SIDE - MARGINS, HEIGHT_TITLE)
        x_center = (WIDTH_PLAYER_SIDE + MARGINS) // 2
        render_text(self.screen, 'CATANE', x_center, HEIGHT_TITLE // 2 - 3, 130, (50, 50, 50))
        if self.game.game_state == GameState.PLACING_COLONIES:
            text = 'Placement'
        elif self.game.game_state == GameState.PLAYING:
            text = "Jeu"
        else:  # self.game.game_state == GameState.END
            text = "Fin"
        render_text(self.screen, text, x_center, HEIGHT_TITLE // 2 + 50, 52, (50, 50, 50))

    def render_actions_box(self):
        x, y, width, height = MARGINS, 2 * MARGINS + HEIGHT_TITLE, WIDTH_PLAYER_SIDE - MARGINS, HEIGHT_ACTIONS_BOX

        self.rectangle(x, y, width, height)
        button = False
        dices = self.game.dices
        current_player = self.game.get_current_player()
        my_turn = (self.main_player == current_player)
        if self.game.game_state == GameState.PLACING_COLONIES:
            dices = None
            text = "Vous devez" if my_turn else f"{current_player.nickname} doit"
            if self.game.game_sub_state == GamePlacingColoniesState.PLACING_COLONY:
                text += " construire une colonie."
            else:  # self.game.game_sub_state == GamePlacingColoniesState.PLACING_ROAD:
                text += " construire une route."
        else:
            if self.game.game_sub_state == GamePlayingState.THROW_DICES:
                dices = (0, 0)
                if my_turn:
                    button = True
                    text = "Lancer les dés"
                else:
                    text = f"{current_player.nickname} lance les dés..."
            elif self.game.game_sub_state == GamePlayingState.GET_RESOURCES:
                if my_turn:
                    button = True
                    text = "Récupérer les ressources"
                else:
                    text = f"{current_player.nickname} récupère les ressources..."
            elif self.game.game_sub_state == GamePlayingState.NEXT_TURN:
                if my_turn:
                    button = True
                    text = "Fin du tour"
                else:
                    text = f"{current_player.nickname} est en train de jouer..."
            else:
                text = "Vous devez" if my_turn else f"{current_player.nickname} doit"
                if self.game.game_sub_state == GamePlayingState.MOVE_THIEF:
                    text += " déplacer le voleur."
                else:  # self.game.game_sub_state == GamePlayingState.STEAL_CARD:
                    text += " voler une carte."

        if dices:
            m = (HEIGHT_ACTIONS_BOX - SIZE_DICE) // 2
            self.render_dice(MARGINS + m, y + m, dices[0])
            self.render_dice(MARGINS + 2 * m + SIZE_DICE, y + m, dices[1])
            x_center = (x_position_after_dice() + WIDTH_PLAYER_SIDE) // 2
        else:
            x_center = (MARGINS + WIDTH_PLAYER_SIDE) // 2

        if button:
            x_button, y_button = position_button_action()
            self.button(x_button, y_button, WIDTH_BUTTON_ACTION, HEIGHT_BUTTON_ACTION, text, 30,
                        (0, 0, 0), (0, 0, 0), (190, 190, 190))
        else:
            color = (0, 0, 0) if current_player.color == Color.WHITE else current_player.color.value
            render_text(self.screen, text, x_center, y + height // 2, 35, color)

    def render_buttons_main_player(self, x: int, y: int, width: int, height: int):
        pass  # TODO

    def render_players(self):
        y_players = HEIGHT_TITLE + HEIGHT_ACTIONS_BOX + 3 * MARGINS
        size_secondary_player = (HEIGHT - y_players) // 3 - MARGINS

        self.game.board.render(WIDTH_PLAYER_SIDE + 10, Y_BOARD, self.screen)
        y = y_players
        for i, player in enumerate(self.game.players):
            if player == self.main_player:
                self.render_player_main(2 * MARGINS + size_secondary_player, y_players,
                                        WIDTH_PLAYER_SIDE - 2 * MARGINS - size_secondary_player,
                                        HEIGHT - y_players - MARGINS)
            else:
                self.render_player_secondary(player, MARGINS, y, size_secondary_player, size_secondary_player)
                y += MARGINS + size_secondary_player

    def render_player_shared(self, player: Player, x: int, y: int, width: int, height: int):
        self.rectangle(x, y, width, height)
        m = 5
        self.screen.fill(player.color.value, (x + m, y + m, ResourceManager.PLAYER_LOGO.get_width(),
                                              ResourceManager.PLAYER_LOGO.get_height()))
        self.screen.blit(ResourceManager.PLAYER_LOGO, (x + m, y + m))

    def render_player_main(self, x: int, y: int, width: int, height: int):
        # Rectangle and player logo
        self.render_player_shared(self.main_player, x, y, width, height)

        # Nickname
        color = (0, 0, 0) if self.main_player.color == Color.WHITE else self.main_player.color.value
        render_text(self.screen, self.main_player.nickname.upper(), x + 8 + ResourceManager.PLAYER_LOGO.get_width(),
                    y + (ResourceManager.PLAYER_LOGO.get_height() - 34 // 2) // 2 + 5, 34, color, centred=False)

        # Buttons
        self.render_buttons_main_player(x, y + Y_BUTTONS_IN_MAIN_PLAYER_BOX, width, HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX)

        # Victory points
        m = 5
        n = (NUM_VICTORY_POINTS_FOR_VICTORY + 1) // 2
        x_victory_points = x + width - (ResourceManager.SMALL_CROWN.get_width() + m) * n
        img_victory_points = ResourceManager.SMALL_CROWN
        num_victory_points = self.main_player.num_victory_points()
        for j in range(2):
            for i in range(n):
                if n * j + i == num_victory_points:
                    img_victory_points = ResourceManager.SMALL_CROWN_GRAY
                self.screen.blit(img_victory_points, (x_victory_points + (img_victory_points.get_width() + m) * i,
                                                      y + m + (img_victory_points.get_height() + m) * j))

        # Resource cards
        self.render_cards(list(self.main_player.resource_cards.list_resources()), x + width // 2, y + 310, 90)

        # Dev_card
        y_construction = y + Y_BUTTONS_IN_MAIN_PLAYER_BOX + HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX
        self.render_cards(self.main_player.dev_cards, x + 126 + (width - 126) // 2, y_construction + 10 + 260, 50)

        # Constructions and dev cards
        height_constructions = (height + y - y_construction) // 4 - 3
        y_construction += height_constructions // 2
        for image, text in [(ResourceManager.CONSTRUCTIONS[construction][self.main_player.color],
                             f"{self.main_player.num_constructions_belonging_to_player(construction)}/"
                             f"{NUM_CONSTRUCTION_MAX[construction]}")
                            for construction in [ConstructionKind.ROAD, ConstructionKind.COLONY,
                                                 ConstructionKind.TOWN]] + [(ResourceManager.SMALL_DEV_CARD,
                                                                             str(self.main_player.num_knights()))]:
            self.screen.blit(image, (x + 35 - image.get_width() // 2, y_construction - image.get_height() // 2))
            render_text(self.screen, text, x + 100, y_construction, 40)

            y_construction += height_constructions

    def render_player_secondary(self, player: Player, x: int, y: int, width: int, height: int):
        # Rectangle and player logo
        self.render_player_shared(player, x, y, width, height)

        # Nickname
        color = (0, 0, 0) if player.color == Color.WHITE else player.color.value
        render_text(self.screen, player.nickname.upper(),
                    x + (height + ResourceManager.PLAYER_LOGO.get_width()) // 2,
                    y + ResourceManager.PLAYER_LOGO.get_height() // 2 + 5, 28, color)

        # Resource cards
        x_cards, y_cards = x + 3, y + 5 + ResourceManager.PLAYER_LOGO.get_height()
        self.screen.blit(ResourceManager.BACK_CARD, (x_cards, y_cards))
        render_text(self.screen, str(sum(player.resource_cards.values())),
                    x_cards + ResourceManager.BACK_CARD.get_width() // 2,
                    y_cards + ResourceManager.BACK_CARD.get_height() // 2, 60)

        # Victory points
        x_victory_points = x + (ResourceManager.BACK_CARD.get_width() + height - ResourceManager.CROWN.get_width()) // 2
        y_victory_points = y + ResourceManager.PLAYER_LOGO.get_height()
        self.screen.blit(ResourceManager.CROWN, (x_victory_points, y_victory_points))
        render_text(self.screen, str(player.num_victory_points()),
                    x_victory_points + ResourceManager.CROWN.get_width() // 2,
                    y_victory_points + ResourceManager.CROWN.get_height() // 2 + 2, 35)

        # Dev cards
        y_small_cards = y_cards + ResourceManager.CARD_HEIGHT - ResourceManager.SMALL_DEV_CARD.get_height()
        x_small_card_1 = x + ResourceManager.CARD_WIDTH
        x_small_card_2 = x + height - ResourceManager.SMALL_KNIGHT_CARD.get_width() - 3
        self.screen.blit(ResourceManager.SMALL_DEV_CARD, (x_small_card_1, y_small_cards))
        self.screen.blit(ResourceManager.SMALL_KNIGHT_CARD, (x_small_card_2, y_small_cards))
        render_text(self.screen, str(len(player.dev_cards)),
                    x_small_card_1 + ResourceManager.SMALL_DEV_CARD.get_width() // 2,
                    y_small_cards + ResourceManager.SMALL_DEV_CARD.get_height() // 2, 35)
        render_text(self.screen, str(player.num_knights()),
                    x_small_card_2 + ResourceManager.SMALL_KNIGHT_CARD.get_width() // 2,
                    y_small_cards + ResourceManager.SMALL_KNIGHT_CARD.get_height() // 2, 35)