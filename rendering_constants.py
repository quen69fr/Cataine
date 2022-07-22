
from typing import Generator

from resource_manager import ResourceManager


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

ANGLE_BETWEEN_CARDS_MAX = 13
RADIUS_CARDS_HAND = 200
RADIUS_CARDS_HAND_SELECTED = 215
ANGLE_MAX_CARDS_RESOURCE = 90
ANGLE_MAX_CARDS_DEV_AND_EXCHANGE = 50

WIDTH_EXCHANGE_BOX = 500
HEIGHT_EXCHANGE_BOX = 230
HEIGHT_BUTTONS_EXCHANGE_BOX = 40
Y_CARDS_IN_EXCHANGE_BOX = 300


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


def dim_bank_resource() -> (int, int):
    return 5 * ResourceManager.CARD_WIDTH + 6 * MARGINS, ResourceManager.CARD_HEIGHT + 2 * MARGINS


def position_bank_resource_exchange() -> (int, int):
    x, y, w, h = rect_buttons_main_player()[1]
    _, height = dim_bank_resource()
    return x + w + MARGINS, y + (h - height) // 2


def position_exchange_box() -> (int, int):
    x, y, w, h = rect_buttons_main_player()[2]
    return x + w + MARGINS, y + (h - HEIGHT_EXCHANGE_BOX) // 2


def xs_cards_exchange_box() -> (int, int):
    x, _ = position_exchange_box()
    return x + WIDTH_EXCHANGE_BOX // 4, x + WIDTH_EXCHANGE_BOX - WIDTH_EXCHANGE_BOX // 4


def rect_buttons_exchange_box() -> list[tuple[int, int, int, int]]:
    width = (WIDTH_EXCHANGE_BOX - 3 * MARGINS) // 2
    x, y = position_exchange_box()
    y += HEIGHT_EXCHANGE_BOX - HEIGHT_BUTTONS_EXCHANGE_BOX - MARGINS
    return [(x + MARGINS, y, width, HEIGHT_BUTTONS_EXCHANGE_BOX),
            (x + 2 * MARGINS + width, y, width, HEIGHT_BUTTONS_EXCHANGE_BOX)]


def position_resources_exchange_box() -> (int, int):
    _, y = position_exchange_box()
    x = xs_cards_exchange_box()[1]
    width, height = dim_bank_resource()
    return x - width // 2, y - height + MARGINS
