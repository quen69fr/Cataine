from __future__ import annotations

import pygame

from tile_intersection import TileIntersection


class TilePath:
    def __init__(self, intersections: list[TileIntersection]):
        self.intersections = intersections
        self.road = False
        self.port = None  # TODO

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        pygame.draw.line(screen, pygame.Color("blue"), start, end, 1)
        print(start, end)