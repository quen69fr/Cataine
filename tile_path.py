from __future__ import annotations

import pygame.gfxdraw
from math import pi, cos, sin

from tile_intersection import TileIntersection
from resource_manager import ResourceManager
from resource import Resource
from color import Color, COLOR_ROAD_EDGES


class TilePath:
    def __init__(self, intersections: list[TileIntersection]):
        self.intersections = intersections
        self.road: Color | None = None  # TODO : Player
        self.port: tuple[Resource, int] | None = None

    def add_port(self, res: Resource, direction: int):
        self.port = (res, direction)

    def render_port(self, x0: int, y0: int, screen: pygame.Surface):
        if self.port is None:
            return
        res, direction = self.port
        img = pygame.transform.rotate(ResourceManager.PORTS[res], direction)
        w, h = img.get_size()

        x1, y1 = self.intersections[0].position(x0, y0)
        x2, y2 = self.intersections[1].position(x0, y0)

        rad = direction * pi / 180
        x = (x1 + x2 + cos(rad) * ResourceManager.TILE_PATH_LENGTH - w) / 2
        y = (y1 + y2 - sin(rad) * ResourceManager.TILE_PATH_LENGTH - h) / 2

        screen.blit(img, (x, y))

    def render_first_layer(self, x0: int, y0: int, screen: pygame.Surface):
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        if self.road is None:
            pygame.draw.aaline(screen, COLOR_ROAD_EDGES, start, end, 1)
        else:
            pygame.draw.line(screen, COLOR_ROAD_EDGES, start, end, ResourceManager.ROAD_WIDTH + 2)
            pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                         ResourceManager.ROAD_WIDTH // 2, COLOR_ROAD_EDGES)
            pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                         ResourceManager.ROAD_WIDTH // 2, COLOR_ROAD_EDGES)

    def render_second_layer(self, x0: int, y0: int, screen: pygame.Surface):
        if self.road is None:
            return
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        pygame.draw.line(screen, self.road.value, start, end, ResourceManager.ROAD_WIDTH - 2)
        pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road.value)
        pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road.value)
