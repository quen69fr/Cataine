from __future__ import annotations

import random

import pygame

from game import Game
from resource_manager import ResourceManager

random.seed(1)
pygame.init()

background = pygame.image.load("images/FondEau.png")
screen = pygame.display.set_mode(background.get_size())
clock = pygame.time.Clock()

ResourceManager.load()

game = Game()


def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.halfturn()
                elif event.key == pygame.K_ESCAPE:
                    return

        screen.blit(background, (0, 0))
        game.render(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
