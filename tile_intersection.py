from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from construction import Construction
from resource_manager import ResourceManager

if TYPE_CHECKING:
    from tile import Tile
    from tile_path import TilePath


class TileIntersection:
    def __init__(self, x: int, y: int, neighbour_paths: list[TilePath] = None, neighbour_tiles: list[Tile] = None):
        self.content: Construction | None = None
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
        img = ResourceManager.CONSTRUCTIONS[self.content.kind][self.content.player.color]
        screen.blit(img, (x - img.get_width() / 2, y - img.get_height() / 2))

    def position(self, x0: int, y0: int):
        x = x0 + self.x * (ResourceManager.TILE_WIDTH/2)
        y = y0 + (ResourceManager.TILE_HEIGHT - ResourceManager.TILE_HAT_HEIGHT) * (self.y // 2) + \
            ResourceManager.TILE_HAT_HEIGHT * (self.y % 2)
        return x, y

    def can_build(self):
        for p in self.neighbour_paths:
            for t in p.intersections:
                if t.content is not None:
                    return False
        return True

    def neighbour_paths_intersection(self):
        for path in self.neighbour_paths:
            for inte in path.intersections:
                if inte != self:
                    yield path, inte
