
from __future__ import annotations

import pygame

from resource import Resource
from resource_manager import ResourceManager
from tile_intersection import TileIntersection


class Tile:
    def __init__(self, res: Resource, x: int, y: int, dice_number: int, intersections: list[TileIntersection] = None):
        self.resource = res
        self.x = x
        self.y = y
        if intersections is None:
            intersections = []
        self.intersections = intersections
        self.dice_number = dice_number

    def add_intersection(self, intersection: TileIntersection):
        self.intersections.append(intersection)

    def render(self, x0: int, y0: int, screen: pygame.Surface, has_thief: bool = False):
        x, y = self.position(x0, y0)
        screen.blit(ResourceManager.TILES[self.resource], (x, y))
        if not self.resource == Resource.DESERT:
            screen.blit(ResourceManager.DICE_NUMBER_IMAGE[self.dice_number],
                        (x + ResourceManager.TILE_WIDTH / 2 - ResourceManager.DICE_NUMBER_RADIUS,
                         y + ResourceManager.TILE_HEIGHT / 2 - ResourceManager.DICE_NUMBER_RADIUS))
        if has_thief:
            img = ResourceManager.THIEF_IMAGE_WITH_DICE_NUMBER
            if self.resource == Resource.DESERT:
                img = ResourceManager.THIEF_IMAGE
            screen.blit(img, (x + ResourceManager.TILE_WIDTH / 2 - img.get_width() / 2,
                              y + ResourceManager.TILE_HEIGHT / 2 - img.get_height() / 2))

    def position(self, x0: int, y0: int):
        return (x0 + self.x * ResourceManager.TILE_WIDTH / 2,
                y0 + self.y / 2 * (ResourceManager.TILE_HEIGHT - ResourceManager.TILE_HAT_HEIGHT))