from __future__ import annotations

import pygame

from resource import BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS
from board import Board
from resource_manager import ResourceManager


pygame.init()

screen = pygame.display.set_mode((760, 760))
srect = screen.get_rect()

clock = pygame.time.Clock()

board = Board(BOARD_LAYOUT_RESOURCES, BOARD_LAYOUT_DICE_NUMBERS)

ResourceManager.load()


def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        board.render(50, 50, screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
