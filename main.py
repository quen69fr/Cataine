from __future__ import annotations

import pygame

from resource_manager import ResourceManager
from game import Game
from strategy import Strategy
from strategy_with_objectives import StrategyWithObjectives
from strategy_neural_network import StrategyNeuralNetwork
from render_game import RenderGame
from player import Player, PlayerManager
from ia_player import IaPlayer
from manual_player import ManualPlayer
import json


if __name__ == "__main__":
    play_against_computer = True
    ia_play_with_space = False

    # random.seed(1)
    pygame.init()
    clock = pygame.time.Clock()

    ResourceManager.load()

    if play_against_computer:
        # game = Game(["Mathieu", "Quentin", "Juliette", "Sarah"])
        game = Game(["Joueur", "Ordi 1", "Ordi 2", "Ordi 3"])

        player_managers: dict[Player, PlayerManager] = {
            player: IaPlayer(player, StrategyWithObjectives(game.board, player)) for player in game.players
        }
        player_managers[game.players[0]] = ManualPlayer(game.players[0], auto_refuse_ratio_max_exchange=0.5)

        Strategy.exchange_with_others = True
    else:
        game = Game(["Network 1", "Network 2", "Network 3", "Network 4"])

        player_managers: dict[Player, PlayerManager] = {
            player: IaPlayer(player, StrategyNeuralNetwork(game.board, player)) for player in game.players
        }

        with open("neural_network_training_data/old_60_networks_training/generations_long_games_2/"
                  "networks_gen_50.json") as file:
            neural_network_players = json.load(file)
        with open("neural_network_training_data/old_60_networks_training/generations_long_games_2/"
                  "marks_gen_50.json") as file:
            neural_network_marks = json.load(file)

        best_player_networks = []
        for _ in range(4):
            m = max(neural_network_marks)
            i = neural_network_marks.index(m)
            neural_network_marks.pop(i)
            best_player_networks.append(neural_network_players.pop(i))

        for player_manager, network in zip(player_managers.values(), best_player_networks):
            if isinstance(player_manager, IaPlayer) and \
                    isinstance(player_manager.strategy, StrategyNeuralNetwork):
                player_manager.strategy.from_list_network(network)

    render_game = RenderGame(game, game.players[0], player_managers[game.players[0]])

    running = True

    while running:
        for player_manager in player_managers.values():
            if isinstance(player_manager, ManualPlayer):
                player_manager.clic = False
            elif ia_play_with_space and isinstance(player_manager, IaPlayer):
                player_manager.play_next_step = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if ia_play_with_space:
                        for player_manager in player_managers.values():
                            if isinstance(player_manager, IaPlayer):
                                player_manager.play_next_step = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_TAB:
                    new_player = game.players[(game.players.index(render_game.main_player) + 1) % len(game.players)]
                    render_game.change_main_player(new_player, player_managers[new_player])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                render_game.clic_event()

        game.play(player_managers)
        render_game.render()
        render_game.update_rendering()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
