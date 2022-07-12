
import pygame

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

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        pass  # TODO
