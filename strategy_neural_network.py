from __future__ import annotations

import json
import numpy as np
from math import tanh
from typing import TYPE_CHECKING
from random import shuffle, random

from strategy import Strategy
from board import Board
from resource import ORDER_RESOURCES
from dev_cards import ORDER_DEV_CARD
from construction import Construction, ConstructionKind
from actions import Action, ActionBuildColony, ActionBuildRoad, ActionBuildTown
from exchange import Exchange, BANK_PLAYER_FOR_EXCHANGE

if TYPE_CHECKING:
    from player import Player


def squeeze_function(x: float):
    return 1 / (1 + np.exp(-x))


v_squeeze_function = np.vectorize(squeeze_function)


def squeeze_function_derivative(x: float):
    e = np.exp(-x)
    return e / ((1 + e) ** 2)


v_squeeze_function_derivative = np.vectorize(squeeze_function_derivative)


class StrategyNeuralNetworkBrutal(Strategy):
    """
    Trained for a specific initial board
    Without dev cards (for now !)
    Without exchanges between players
    """

    def __init__(self, board: Board, player: Player):
        Strategy.__init__(self, board, player)

        board_vector_size = len(self.board.tiles) + 2 * (len(self.board.intersections) + len(self.board.paths))
        #                 = 271
        player_vector_size = len(ORDER_DEV_CARD) + len(ORDER_RESOURCES)
        #                  = 16
        input_size = board_vector_size + player_vector_size + 1  # 1 for can_steal_card
        #          = 287

        self.layers: list[int] = [input_size, 30, 8, 1]

        self.weights: np.array = [np.random.uniform(-1., 1., (n2, n1))
                                  for n1, n2 in zip(self.layers[:-1], self.layers[1:])]
        self.biases: np.array = [np.random.uniform(-1., 1., (n, 1)) for n in self.layers[1:]]

    def play(self):
        best_mark = self._mark_game_state()
        while True:
            best_action_or_exchange: Action | Exchange | None = None
            for action in self.player.get_all_possible_one_shot_actions(include_dev_card=False):
                self._fake_action(action)
                mark = self._mark_game_state()
                self._unfake_action(action)
                if mark > best_mark:
                    best_action_or_exchange = action
                    best_mark = mark
            for exchange in self.player.get_all_possible_exchanges_with_the_bank():
                exchange.apply_one(self.player)
                mark = self._mark_game_state()
                exchange.undo(self.player)
                if mark > best_mark:
                    best_action_or_exchange = exchange
                    best_mark = mark
            if best_action_or_exchange is None:
                return True
            if isinstance(best_action_or_exchange, Action):
                best_action_or_exchange.apply()
            elif isinstance(best_action_or_exchange, Exchange):
                best_action_or_exchange.apply(self.player, BANK_PLAYER_FOR_EXCHANGE)

    def place_initial_colony(self):
        best_mark = 0
        best_inter = None
        for inter in self.board.intersections:
            if not inter.can_build():
                continue
            inter.content = Construction(ConstructionKind.COLONY, self.player)
            mark = self._mark_game_state()
            inter.content = None
            if mark > best_mark:
                best_inter = inter
                best_mark = mark
        return best_inter

    def place_road_around_initial_colony(self):
        inter = self.player.get_initial_colony_intersection_without_road()
        best_mark = 0
        best_path = None
        for path in inter.neighbour_paths:
            path.road_player = self.player
            mark = self._mark_game_state()
            path.road_player = None
            if mark > best_mark:
                best_path = path
                best_mark = mark
        return best_path

    def _fake_action(self, action: Action):
        self.player.consume_resources(action.cost)
        if isinstance(action, ActionBuildRoad):
            action.path.road_player = self.player
        elif isinstance(action, ActionBuildColony):
            action.intersection.content = Construction(ConstructionKind.COLONY, self.player)
        elif isinstance(action, ActionBuildTown):
            action.intersection.content = Construction(ConstructionKind.TOWN, self.player)

    def _unfake_action(self, action: Action):
        self.player.add_resources(action.cost)
        if isinstance(action, ActionBuildRoad):
            action.path.road_player = None
        elif isinstance(action, ActionBuildColony):
            action.intersection.content = None
        elif isinstance(action, ActionBuildTown):
            action.intersection.content = Construction(ConstructionKind.COLONY, self.player)

    def remove_cards_thief(self, num_cards_kept: int):
        best_resource_cards = None
        best_mark = 0
        old_hand = self.player.resource_cards
        for resource_cards in self.player.resource_cards.copy().subsets_of_size_k(num_cards_kept):
            self.player.resource_cards = resource_cards
            mark = self._mark_game_state()
            if mark > best_mark:
                best_resource_cards = resource_cards
                best_mark = mark
        self.player.resource_cards = old_hand
        assert best_resource_cards is not None
        return best_resource_cards

    def move_thief(self):
        best_mark = 0
        best_tile = None
        for tile in self.board.tiles:
            if tile == self.board.thief_tile:
                continue
            old_tile = self.board.thief_tile
            self.board.thief_tile = tile
            mark = self._mark_game_state(can_steal_card=self.player.can_steal())
            if mark > best_mark:
                best_tile = tile
                best_mark = mark
            self.board.thief_tile = old_tile
        return best_tile

    def steal_card(self):
        # TODO : When we would take care of the other players of the game state vectorisation...
        for inter in self.board.thief_tile.intersections:
            if inter.content is None:
                continue
            player = inter.content.player
            if player == self.player or player.num_resources() == 0:
                continue
            return player
        assert False

    def accept_exchange(self, exchange: Exchange):
        return False

    def _mark_game_state(self, can_steal_card: bool = False):
        return float(self._feedforward(self._game_state_to_vector(can_steal_card=can_steal_card)))

    def _game_state_to_vector(self, can_steal_card: bool = False):
        # TODO : Infos on the other players...
        return np.concatenate([self._board_to_vector(), self._player_to_vector(),
                               np.array([[1 if can_steal_card else 0]])])

    def get_game_state_to_vector(self):
        return self._game_state_to_vector(self.player.can_steal())

    def _board_to_vector(self):
        return np.concatenate([self._intersections_to_vector(), self._paths_to_vector(), self._thief_to_vector()])

    def _intersections_to_vector(self):
        v_player = np.zeros((len(self.board.intersections), 1))
        v_others = np.zeros((len(self.board.intersections), 1))
        for i, inter in enumerate(self.board.intersections):
            if inter.content is None:
                continue
            if inter.content.player == self.player:
                v_player[i] = 1 if inter.content.kind == ConstructionKind.TOWN else 0.5
            else:
                v_others[i] = 1 if inter.content.kind == ConstructionKind.TOWN else 0.5
        return np.concatenate([v_player, v_others])

    def _paths_to_vector(self):
        return np.concatenate([np.array([[1 if path.road_player == self.player else 0] for path in self.board.paths]),
                               np.array([[1 if path.road_player is None else 0] for path in self.board.paths])])

    def _thief_to_vector(self):
        v = np.zeros((len(self.board.tiles), 1))
        v[self.board.tiles.index(self.board.thief_tile)] = 1
        return v

    def _player_to_vector(self):
        return np.concatenate([self._hand_resources_to_vector(), self._hand_dev_cards_to_vector()])

    def _hand_resources_to_vector(self):
        return np.array([[tanh(self.player.resource_cards[res])] for res in ORDER_RESOURCES])

    def _hand_dev_cards_to_vector(self):
        return np.array([[tanh(self.player.dev_cards.count(dev))] for i, dev in enumerate(ORDER_DEV_CARD)])

    # -------------------------------------------------------------------------

    def from_list_network(self, params: list):
        self.weights = [np.array(weight) for weight in params[0]]
        self.biases = [np.array(bias) for bias in params[1]]

    def to_list_network(self) -> list:
        return [[weight.tolist() for weight in self.weights], [bias.tolist() for bias in self.biases]]

    def save_network(self, path: str):
        with open(path, "w") as file:
            json.dump(self.to_list_network(), file)

    def load_network(self, path: str):
        with open(path, "r") as file:
            params = json.load(file)
        self.from_list_network(params)

    def _feedforward(self, layer: np.array):
        for i, weight in enumerate(self.weights):
            layer = np.dot(weight, layer) + self.biases[i]
            layer = v_squeeze_function(layer)
        return layer

    def _backpropagation(self, layer: np.array, answer: float):
        # feedforward
        neurons = []
        neurons_squeezed = [layer]
        for i, weight in enumerate(self.weights):
            layer = np.dot(weight, layer) + self.biases[i]
            neurons.append(layer)
            layer = v_squeeze_function(layer)
            neurons_squeezed.append(layer)

        # backpropagation
        delta_neurons = v_squeeze_function_derivative(neurons[-1]) * (np.array([[answer]]) - neurons_squeezed[-1])
        delta_weights = [np.dot(delta_neurons, neurons_squeezed[-2].transpose())]
        delta_biases = [delta_neurons]

        for idx in range(2, len(self.layers)):
            delta_neurons = v_squeeze_function_derivative(neurons[-idx]) * \
                            np.dot(self.weights[-idx + 1].transpose(), delta_neurons)
            delta_biases.insert(0, delta_neurons)
            delta_weights.insert(0, np.dot(delta_neurons, neurons_squeezed[-idx - 1].transpose()))

        return delta_weights, delta_biases

    def _training_step(self, data: list[tuple[np.array, float]], coef_step: float):
        delta_weights = [np.zeros(weight.shape) for weight in self.weights]
        delta_biases = [np.zeros(bias.shape) for bias in self.biases]
        for layer, answer in data:
            single_delta_weights, single_delta_biases = self._backpropagation(layer, answer)
            delta_weights = [delta_weight + single_delta_weight
                             for delta_weight, single_delta_weight in zip(delta_weights, single_delta_weights)]
            delta_biases = [delta_bias + single_delta_bias
                            for delta_bias, single_delta_bias in zip(delta_biases, single_delta_biases)]
        coef = coef_step / len(data)
        self.weights = [weight + coef * delta_weight for weight, delta_weight in zip(self.weights, delta_weights)]
        self.biases = [bias + coef * delta_bias for bias, delta_bias in zip(self.biases, delta_biases)]

    def train_network(self, training_data: list[tuple[np.array, float]], list_num_data: list,
                      list_num_steps: list, list_coef_step: list):
        shuffle(training_data)
        num_tot_data = len(training_data)
        idx = 0
        for num_steps, num_data, coef_step in zip(list_num_steps, list_num_data, list_coef_step):
            for _ in range(num_steps):
                if idx + num_data > num_tot_data:
                    step_data = training_data[idx:num_tot_data]
                    shuffle(training_data)
                    idx = idx + num_data - num_tot_data
                    self._training_step(step_data + training_data[0:idx], coef_step)
                else:
                    self._training_step(training_data[idx:idx + num_data], coef_step)
                    idx += num_data

        # for num_steps, num_data, coef_step in zip(list_num_steps, list_num_data, list_coef_step):
        #     for _ in range(num_steps):
        #         shuffle(training_data)
        #         self._training_step(training_data[:num_data], coef_step)

    def accuracy(self, training_data: list[tuple[np.array, float]]):
        mark = 0.
        for layer, answer in training_data:
            mark += (float(self._feedforward(layer)) - answer) ** 2
        return mark ** 0.5 / len(training_data)

    def inherit(self, parents: list[StrategyNeuralNetworkBrutal],
                proba_mutation: float = 0., mutation_scale: float = 0.):
        self.weights = [np.array([[float(sum(parent.weights[n][j][i] for parent in parents) / len(parents)) +
                                   ((2 * random() - 1) * mutation_scale if random() < proba_mutation else 0)
                                   for i in range(n1)] for j in range(n2)])
                        for n, (n1, n2) in enumerate(zip(self.layers[:-1], self.layers[1:]))]
        self.biases = [np.array([[float(sum(parent.biases[i][j] for parent in parents) / len(parents)) +
                                  ((2 * random() - 1) * mutation_scale if random() < proba_mutation else 0)]
                                 for j in range(n)])
                       for i, n in enumerate(self.layers[1:])]
