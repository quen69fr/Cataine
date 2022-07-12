
import pygame

from constants import *

# from tile import Tile
# from tile_path import TilePath


class TileIntersection:
    # def __init__(self, neighbour_paths: list[TilePath] = None, neighbour_tiles: list[Tile] = None):
    def __init__(self, x: int, y: int, neighbour_paths: list = None, neighbour_tiles: list = None):
        self.content = None
        self.x = x
        self.y = y
        if neighbour_paths is None:
            neighbour_paths = []
        if neighbour_tiles is None:
            neighbour_tiles = []
        self.neighbour_paths = neighbour_paths
        self.neighbour_tiles = neighbour_tiles

    # def add_neighbour_path(self, neighbour_path: TilePath):
    def add_neighbour_path(self, neighbour_path):
        self.neighbour_paths.append(neighbour_path)

    # def add_neighbour_tile(self, neighbour_tile: Tile):
    def add_neighbour_tile(self, neighbour_tile):
        self.neighbour_tiles.append(neighbour_tile)

    def render(self, x0: int, y0: int, screen: pygame.Surface, i):
        x, y = self.position(x0, y0)
        # pygame.draw.circle(screen, pygame.Color("red"), (x, y), 10)
        font = pygame.font.Font(None, 20)
        surf = font.render(str(i), True, pygame.Color("red"))
        screen.blit(surf, (x, y))

    def position(self, x0, y0):
        x = x0 + self.x * (TILE_WIDTH/2)
        a = TILE_HEIGHT - 38
        b = 38
        y = y0 + a * (self.y // 2) + b * (self.y % 2)
        return x, y
