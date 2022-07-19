
from enum import Enum


class DevCard(Enum):
    KNIGHT = 0
    MONOPOLY = 1
    FREE_ROADS = 2
    FREE_CARDS = 3
    VICTORY_POINT = 4


NUM_DEV_CARDS = {
    DevCard.KNIGHT: 14,
    DevCard.MONOPOLY: 2,
    DevCard.FREE_ROADS: 2,
    DevCard.FREE_CARDS: 2,
    DevCard.VICTORY_POINT: 5
}
