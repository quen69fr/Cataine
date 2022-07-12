
import pygame

from tile_intersection import TileIntersection


class TilePath:
    def __init__(self, intersections: list[TileIntersection]):
        self.intersections = intersections
        self.road = False
        self.port = None  # TODO

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        pass  # TODO
