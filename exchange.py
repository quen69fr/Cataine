
from dataclasses import dataclass
from resource_hand_count import ResourceHandCount
from typing import TYPE_CHECKING

from logs import log
if TYPE_CHECKING:
    from player import Player


BANK_PLAYER_FOR_EXCHANGE = 0


@dataclass
class Exchange:
    gain: ResourceHandCount
    lost: ResourceHandCount

    def inverse(self):
        return Exchange(self.lost, self.gain)

    def possible(self, player: 'Player'):
        return player.has_resources(self.lost)

    def apply(self, player: 'Player', other_player: 'player | BANK_PLAYER_FOR_EXCHANGE'):
        log(f"Exchange between {player} and "
            f"{'the bank' if other_player == BANK_PLAYER_FOR_EXCHANGE else str(other_player)}: {self}")
        self.apply_one(player)
        if not other_player == BANK_PLAYER_FOR_EXCHANGE:
            self.inverse().apply_one(other_player)

    def apply_one(self, player: 'Player'):
        player.consume_resources(self.lost)
        player.add_resources(self.gain)

    def undo(self, player: 'Player'):
        player.consume_resources(self.gain)
        player.add_resources(self.lost)

    def ratio(self):
        return sum(self.gain.values()) / sum(self.lost.values())
