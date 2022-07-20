from __future__ import annotations

import random

import pygame

from resource_manager import ResourceManager
from game import Game
from render_game import RenderGame

random.seed(1)
pygame.init()
clock = pygame.time.Clock()

ResourceManager.load()

game = Game()
render_game = RenderGame(game)
# pygame.key.set_repeat(250, 10)

# for _ in range(100):
#     game.halfturn()


def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.next_turn_step_ia()
                    # game.complete_turn_ai()
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_TAB:
                    render_game.change_main_player()

        render_game.render()
        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
