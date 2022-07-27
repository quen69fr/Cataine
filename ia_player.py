from __future__ import annotations

from strategy import Strategy
from player import Player, PlayerManager


class IaPlayer(PlayerManager):
    player: Player
    strategy: Strategy

    def __init__(self, player: Player, strategy: Strategy):
        PlayerManager.__init__(self, player)
        self.strategy = strategy

        self.play_next_step = True

    def play(self):
        if not self.play_next_step:
            return False
        return self.strategy.play()

    def place_initial_colony(self):
        if not self.play_next_step:
            return False
        intersection = self.strategy.place_initial_colony()
        self.player.place_initial_colony(intersection)
        return True

    def place_initial_road(self):
        if not self.play_next_step:
            return False
        path = self.strategy.place_road_around_initial_colony()
        self.player.place_initial_road(path)
        return True

    def remove_cards_for_thief(self):
        if not self.play_next_step:
            return False
        if self.player.num_cards_to_remove_for_thief > 0:
            new_hand = self.strategy.remove_cards_thief(self.player.num_resources() -
                                                        self.player.num_cards_to_remove_for_thief)
            self.player.remove_cards_for_thief(new_hand)
        return True

    def move_thief(self):
        if not self.play_next_step:
            return False
        tile = self.strategy.move_thief()
        self.player.move_thief(tile)
        return True

    def steal_card(self):
        if not self.play_next_step:
            return False
        player = self.strategy.steal_card()
        self.player.steal_card(player)
        return True

    def accept_exchange(self) -> bool:
        if not self.play_next_step:
            return False
        assert self.player.exchange_asked is not None
        if self.strategy.accept_exchange(self.player.exchange_asked):
            self.player.accept_exchange()
        else:
            self.player.reject_exchange()
        return True

    def throw_dice(self):
        if not self.play_next_step:
            return False
        return True

    def get_resources(self):
        if not self.play_next_step:
            return False
        return True

    def place_free_road(self):
        pass  # The IA doesn't buy dev card (for now !)

    def free_card(self):
        pass  # The IA doesn't buy dev card (for now !)

    def monopoly(self):
        pass  # The IA doesn't buy dev card (for now !)
