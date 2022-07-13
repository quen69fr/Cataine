from __future__ import annotations

import pygame
from resource_manager import ResourceManager
from color import Color
from construction import Construction

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tile import Tile
    from tile_path import TilePath


class TileIntersection:
    def __init__(self, x: int, y: int, neighbour_paths: list[TilePath] = None, neighbour_tiles: list[Tile] = None):
        self.content: tuple[Construction, Color] | None = None  # TODO : Player
        self.x = x
        self.y = y
        if neighbour_paths is None:
            neighbour_paths = []
        if neighbour_tiles is None:
            neighbour_tiles = []
        self.neighbour_paths = neighbour_paths
        self.neighbour_tiles = neighbour_tiles

    def add_neighbour_path(self, neighbour_path: TilePath):
        self.neighbour_paths.append(neighbour_path)

    def add_neighbour_tile(self, neighbour_tile: Tile):
        self.neighbour_tiles.append(neighbour_tile)

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        if self.content is None:
            return
        x, y = self.position(x0, y0)
        img = ResourceManager.CONSTRUCTIONS[self.content[0]][self.content[1]]
        screen.blit(img, (x - img.get_width() / 2, y - img.get_height() / 2))

    def position(self, x0: int, y0: int):
        x = x0 + self.x * (ResourceManager.TILE_WIDTH/2)
        y = y0 + (ResourceManager.TILE_HEIGHT - ResourceManager.TILE_HAT_HEIGHT) * (self.y // 2) + \
            ResourceManager.TILE_HAT_HEIGHT * (self.y % 2)
        return x, y
