import random
from abc import abstractclassmethod, abstractmethod

from actions import Action
from board import Board
from player import Player


class Strategy:

    @abstractmethod
    def play(self, board: Board, player: Player, all_actions: list[Action]) -> Action:
        pass

class StrategyChooseRandom(Strategy):

    def play(self, board: Board, player: Player, all_actions: list[Action]) -> Action:
        return random.choice(all_actions)
        
