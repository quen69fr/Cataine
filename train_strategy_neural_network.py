from __future__ import annotations

import numpy as np
from typing import Generator
from tqdm import tqdm
import json
import random

from constants import NUM_VICTORY_POINTS_FOR_VICTORY
from game import Game
from strategy import Strategy
from strategy_neural_network import StrategyNeuralNetworkBrutal
from strategy_with_objectives import StrategyWithObjectives
from player import Player
from ia_player import IaPlayer


def generate_infinite_training_data() -> Generator[tuple[np.array, float]]:
    while True:
        game = Game(["Network 1", "Network 2", "ObjStrategy 1", "ObjStrategy 2"])
        strategies_network: dict[Player, StrategyNeuralNetworkBrutal] = {
            player: StrategyNeuralNetworkBrutal(game.board, player) for player in game.players
        }
        strategies: list[Strategy] = [
            strategies_network[game.players[0]],
            strategies_network[game.players[1]],
            StrategyWithObjectives(game.board, game.players[2]),
            StrategyWithObjectives(game.board, game.players[3])
        ]

        player_managers: dict[Player, IaPlayer] = {
            player: IaPlayer(player, strategy) for player, strategy in zip(game.players, strategies)
        }

        for player_manager in player_managers.values():
            player_manager.play_next_step = True

        while not game.end_game():
            player = game.get_current_player()
            game.play(player_managers)
            yield ((strategies_network[player].get_game_state_to_vector(),
                          player.num_victory_points() / NUM_VICTORY_POINTS_FOR_VICTORY))


def create_training_data(num_data: int) -> list[tuple[np.array, float]]:
    generator = generate_infinite_training_data()
    return [next(generator) for _ in tqdm(range(num_data))]


def save_training_data(path: str, data: list[tuple[np.array, float]]):
    with open(path, "w") as file:
        json.dump([[layer.tolist(), answer] for layer, answer in data], file)


def load_training_data(path: str) -> list[tuple[np.array, float]]:
    with open(path, "r") as file:
        params = json.load(file)
    return [(np.array(params[i][0]), params[i][1]) for i in tqdm(range(len(params)))]


def train_strategies(training_data: list[tuple[np.array, float]],
                     strategies_neural_networks: list[StrategyNeuralNetworkBrutal], test_accuracy: bool = False):
    print("Train the neural networks:")
    testing_data = []
    if test_accuracy:
        testing_data = create_training_data(200)
    accuracy_sum = 0.
    accuracy_before = 0.
    for i in tqdm(range(len(strategies_neural_networks))):
        strategy_neural_network = strategies_neural_networks[i]
        if test_accuracy:
            accuracy_before = strategy_neural_network.accuracy(testing_data)
        # strategy_neural_network.train_network(training_data, [10, 50, 100], [2000, 200, 120], [5, 10, 15])
        strategy_neural_network.train_network(training_data, [10], [2000], [5])
        if test_accuracy:
            accuracy_sum += accuracy_before / strategy_neural_network.accuracy(testing_data)
    if test_accuracy:
        print(f"Improvement ratios: {accuracy_sum / len(strategies_neural_networks)}")


if __name__ == "__main__":
    # random.seed(1)
    # print("Creation of the training data:")
    # training_data = create_training_data(50_000)
    # save_training_data("neural_network_training_data/training_data_50000.json", training_data)

    print("Load training data:")
    data = load_training_data("neural_network_training_data/training_data_50000.json")

    temp_game = Game(["Network"])
    strategies = [StrategyNeuralNetworkBrutal(temp_game.board, temp_game.players[0]) for _ in range(100)]
    train_strategies(data, strategies, test_accuracy=True)
