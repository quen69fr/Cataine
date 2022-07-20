
from dataclasses import dataclass
from resource_hand_count import ResourceHandCount
from typing import TYPE_CHECKING

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
        return player.resource_cards.has(self.lost)

    def apply(self, player: 'Player', other_player: 'player | BANK_PLAYER_FOR_EXCHANGE'):
        self.apply_one(player)
        if not other_player == BANK_PLAYER_FOR_EXCHANGE:
            self.inverse().apply_one(other_player)

    def apply_one(self, player: 'Player'):
        player.resource_cards.consume(self.lost)
        player.resource_cards.add(self.gain)

    def undo(self, player: 'Player'):
        player.resource_cards.consume(self.gain)
        player.resource_cards.add(self.lost)
