
import pygame

from tile_intersection import TileIntersection


class Tile:
    def __init__(self, res: int, x: int, y: int, dice_number: int, intersections: list[TileIntersection] = None):
        self.resource = res
        self.x = x
        self.y = y
        if intersections is None:
            intersections = []
        self.intersections = intersections
        self.has_thief = False  # TODO
        self.dice_number = dice_number  # TODO

    def add_intersection(self, intersection: TileIntersection):
        self.intersections.append(intersection)

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        pass  # TODO
