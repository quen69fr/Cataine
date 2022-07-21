
from enum import Enum


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
    REMOVE_CARDS_THIEF = 5


class GamePlacingColoniesState(Enum):
    PLACING_COLONY = 0
    PLACING_ROAD = 1
