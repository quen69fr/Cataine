from __future__ import annotations

import pygame

from resource import BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS, BOARD_PORT_RESOURCES
from board import Board
from resource_manager import ResourceManager


pygame.init()

background = pygame.image.load("images/FondEau.png")

screen = pygame.display.set_mode(background.get_size())
srect = screen.get_rect()

clock = pygame.time.Clock()

board = Board(BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS, BOARD_PORT_RESOURCES)

ResourceManager.load()


def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.blit(background, (0, 0))
        board.render(600, 44, screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
