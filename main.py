from __future__ import annotations

from resource import Resource

import pygame

from board import Board
from resource_manager import ResourceManager

pygame.init()

screen = pygame.display.set_mode((660, 660))
srect = screen.get_rect()

clock = pygame.time.Clock()

board = Board([
    Resource.WOOD,
    Resource.WOOL,
    Resource.WOOL,
    Resource.HAY,
    Resource.ROCK,
    Resource.HAY,
    Resource.WOOD,
    Resource.WOOD,
    Resource.CLAY,
    Resource.DESERT,
    Resource.ROCK,
    Resource.HAY,
    Resource.HAY,
    Resource.ROCK,
    Resource.WOOD,
    Resource.WOOL,
    Resource.CLAY,
    Resource.WOOL,
    Resource.CLAY
], [6,3,8,2,4,5,10,5,9,0,6,9,10,11,3,12,8,4,11])

ResourceManager.load()

def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        board.render(0, 0, screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
