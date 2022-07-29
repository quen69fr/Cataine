from __future__ import annotations

import numpy as np
from typing import Generator
from tqdm import tqdm
import json
from random import shuffle, choices
import matplotlib.pyplot as plt

from constants import NUM_VICTORY_POINTS_FOR_VICTORY
from game import Game
from strategy import Strategy
from strategy_neural_network import StrategyNeuralNetwork
from strategy_with_objectives import StrategyWithObjectives
from player import Player
from ia_player import IaPlayer


def generate_infinite_training_data() -> Generator[tuple[np.array, float]]:
    while True:
        game = Game(["Network 1", "Network 2", "ObjStrategy 1", "ObjStrategy 2"])
        strategies_network: dict[Player, StrategyNeuralNetwork] = {
            player: StrategyNeuralNetwork(game.board, player) for player in game.players
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


class Training:
    game_temp = Game(["A", "B", "C", "D"])

    def __init__(self, strategies_networks: list[StrategyNeuralNetwork] | int | str = 60):
        self.strategies_networks: list[StrategyNeuralNetwork]
        if isinstance(strategies_networks, int):
            self.strategies_networks = [StrategyNeuralNetwork(self.game_temp.board, self.game_temp.players[0])
                                        for _ in range(strategies_networks)]
        elif isinstance(strategies_networks, str):
            self.strategies_networks = self.load_strategies(strategies_networks)
        else:
            self.strategies_networks = strategies_networks

        assert len(self.strategies_networks) % 4 == 0

    def load_strategies(self, path: str) -> list[StrategyNeuralNetwork]:
        with open(path, "r") as file:
            params_list = json.load(file)
        strategies_networks = []
        for i in range(len(params_list)):
            network = StrategyNeuralNetwork(self.game_temp.board, self.game_temp.players[0])
            network.from_list_network(params_list[i])
            strategies_networks.append(network)
        return strategies_networks

    def save_strategies(self, path: str):
        with open(path, "w") as file:
            json.dump([network.to_list_network() for network in self.strategies_networks], file)

    def train_backpropagation(self, training_data: list[tuple[np.array, float]] | int | str):
        training_data: list[tuple[np.array, float]]
        if isinstance(training_data, int):
            print("Create training data:")
            training_data = create_training_data(training_data)
        elif isinstance(training_data, str):
            print("Load training data:")
            training_data = load_training_data(training_data)
        else:
            training_data = training_data

        print("Train the neural networks:")
        for i in tqdm(range(len(self.strategies_networks))):
            # strategy_neural_network.train_network(training_data, [10, 50, 100], [2000, 200, 120], [5, 10, 15])
            self.strategies_networks[i].train_network(training_data, [10], [2000], [5])

    def mark_strategies_networks(self, num_games_per_network: int, num_turns_max: int = 30,
                                 num_victory_points_min: int = 2):
        order = list(range(0, len(self.strategies_networks)))
        marks = np.zeros(len(self.strategies_networks))
        for _ in tqdm(range(num_games_per_network)):
            shuffle(order)
            for i in range(len(self.strategies_networks) // 4):
                game = Game(["A", "B", "C", "D"])

                player_managers: dict[Player, IaPlayer] = {
                    player: IaPlayer(player, self.strategies_networks[order[4 * i + j]])
                    for j, player in enumerate(game.players)
                }

                for j, player in enumerate(game.players):
                    strategy = self.strategies_networks[order[4 * i + j]]
                    strategy.change_of_player_and_board(game.board, player)
                    player_managers[player] = IaPlayer(player, strategy)

                for _ in range(4 * num_turns_max):
                    game.play(player_managers)
                    if game.end_game():
                        break

                for j, player in enumerate(game.players):
                    n = player.num_victory_points(without_longest_road_and_largest_army=True)
                    if n > num_victory_points_min:
                        marks[order[4 * i + j]] += n - num_victory_points_min
                        nb = player.num_bonus_victory_points()
                        if n + nb >= 10:
                            marks[order[4 * i + j]] += nb + 2
        print(f"  -> Marks: - Mean: {marks.mean()}")
        print(f"            - Max: {np.max(marks)}")
        print(f"            - Min: {np.min(marks)}")
        print(f"            - Standard deviation: {marks.std()}")
        return marks

    def compose_new_generation(self, weights: np.array) -> list[StrategyNeuralNetwork]:
        new_generation = []
        for num_descendants, proba, mutation in [
            (20, 0.02, 0.0001),
            (20, 0.002, 0.001),
            (20, 0.0002, 0.01)
        ]:
            for _ in range(num_descendants):
                num_parents = choices([1, 2, 3], [0.9, 0.08, 0.02], k=1)[0]
                network = StrategyNeuralNetwork(self.game_temp.board, self.game_temp.players[0])
                parents = choices(self.strategies_networks, weights, k=num_parents)
                network.inherit(parents, proba, mutation)
                new_generation.append(network)
        return new_generation

    def train_generation(self, num_generations: int = 100, num_games_per_network: int = 50,
                         save_generations: bool = False, matplotlib_figs: bool = False):
        n = 10
        print("Train, select and merge the neural networks:")
        if matplotlib_figs:
            plt.title("Training networks to play Catan")
            plt.xlabel("Generation number")
            plt.ylabel(f"Mark (over {num_games_per_network} games)")
        old_mark_mean = None
        for i_generation in range(num_generations):
            print(f"  -> Generation n°{i_generation + 1}")
            marks = self.mark_strategies_networks(num_games_per_network)
            marks_exp = np.exp(marks)
            self.strategies_networks = self.compose_new_generation(marks_exp / np.sum(marks_exp))
            if matplotlib_figs:
                mark_mean = marks.mean()
                plt.scatter(i_generation * np.ones(len(marks)), marks, s=5, color="blue", alpha=0.1)
                if old_mark_mean is not None:
                    plt.plot([i_generation - 1, i_generation], [old_mark_mean, mark_mean], "k")
                plt.savefig(f"neural_network_training_data/generations_{n}/training_graph.png")
                old_mark_mean = mark_mean
            if save_generations:
                self.save_strategies(f"neural_network_training_data/generations_{n}/"
                                     f"networks_gen_{i_generation + 1}.json")
                with open(f"neural_network_training_data/generations_{n}/"
                          f"marks_gen_{i_generation + 1}.json", "w") as file:
                    json.dump(marks.tolist(), file)


if __name__ == "__main__":
    # random.seed(1)

    # print("Creation of the training data:")
    # training_data = create_training_data(50_000)
    # save_training_data("neural_network_training_data/training_data_50000.json", training_data)

    # training = Training(60)
    # training.train_backpropagation("neural_network_training_data/training_data_50000.json")
    # training.save_strategies("neural_network_training_data/trained_networks_60.json")

    training = Training("neural_network_training_data/trained_networks_60.json")
    training.train_generation(save_generations=True, matplotlib_figs=True)
