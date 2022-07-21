
from typing import Generator


WIDTH = 1360
HEIGHT = 700
MARGINS = 8

WIDTH_PLAYER_SIDE = 615
X_BOARD = 625
Y_BOARD = 44

HEIGHT_TITLE = 130
HEIGHT_ACTIONS_BOX = 80
Y_BUTTONS_IN_MAIN_PLAYER_BOX = 220
HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX = 40
WIDTH_BUTTON_ACTION = 260
HEIGHT_BUTTON_ACTION = 40
SIZE_DICE = 60

ANGLE_BETWEEN_CARDS_MAX = 16
RADIUS_CARDS_HAND = 200
RADIUS_CARDS_HAND_SELECTED = 215
ANGLE_MAX_CARDS_RESOURCE = 90
ANGLE_MAX_CARDS_DEV = 50


def x_position_after_dice() -> int:
    return MARGINS + HEIGHT_ACTIONS_BOX + (HEIGHT_ACTIONS_BOX + SIZE_DICE) // 2


def position_button_action() -> (int, int):
    return ((x_position_after_dice() + WIDTH_PLAYER_SIDE - WIDTH_BUTTON_ACTION) // 2,
            2 * MARGINS + HEIGHT_TITLE + (HEIGHT_ACTIONS_BOX - HEIGHT_BUTTON_ACTION) // 2)


def y_size_secondary_player() -> (int, int):
    y_players = HEIGHT_TITLE + HEIGHT_ACTIONS_BOX + 3 * MARGINS
    return y_players, (HEIGHT - y_players) // 3 - MARGINS


def position_secondary_players(n: int = 3) -> Generator[tuple[int, int], None, None]:
    y_players, size_secondary_player = y_size_secondary_player()
    y = y_players
    for _ in range(n):
        yield MARGINS, y
        y += MARGINS + size_secondary_player


def rect_main_player_box() -> (int, int, int, int):
    y_players, size_secondary_player = y_size_secondary_player()

    return (2 * MARGINS + size_secondary_player, y_players,
            WIDTH_PLAYER_SIDE - 2 * MARGINS - size_secondary_player, HEIGHT - y_players - MARGINS)


def position_hand_resource_cards() -> (int, int):
    x, y, width, _ = rect_main_player_box()
    return x + width // 2, y + 310


def position_hand_dev_cards() -> (int, int):
    x, y, width, _ = rect_main_player_box()
    y_construction = y + Y_BUTTONS_IN_MAIN_PLAYER_BOX + HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX + 5
    return x + 126 + (width - 126) // 2, y_construction + 10 + 260


def rect_buttons_main_player() -> list[tuple[int, int, int, int]]:
    x, y, width, height = rect_main_player_box()
    button_width = (width - 4 * MARGINS - 4) // 3
    y_button = y + Y_BUTTONS_IN_MAIN_PLAYER_BOX

    return [(x + 2 + MARGINS + i * (MARGINS + button_width), y_button,
             button_width, HEIGHT_BUTTONS_IN_MAIN_PLAYER_BOX) for i in range(3)]
