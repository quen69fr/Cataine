from __future__ import annotations

import random
from abc import abstractmethod
from typing import TYPE_CHECKING

from actions import Action
from board import Board

if TYPE_CHECKING:
    from player import Player


class Strategy:

    @abstractmethod
    def play(self, board: Board, player: Player, all_actions: list[Action]) -> Action:
        pass

class StrategyChooseRandom(Strategy):

    def play(self, board: Board, player: Player, all_actions: list[Action]) -> Action:
        print("choose from:", all_actions)
        result = random.choice(all_actions)
        print("  ", result)
        return result
        
