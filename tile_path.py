from __future__ import annotations

from math import cos, pi, sin
from resource import Resource, Port
from typing import TYPE_CHECKING

import pygame.gfxdraw

from resource_manager import ResourceManager
from tile_intersection import TileIntersection

if TYPE_CHECKING:
    from player import Player


class TilePath:
    def __init__(self, intersections: list[TileIntersection]):
        self.intersections = intersections
        self.road_player: Player | None = None
        self.port: Port | None = None

    def add_port(self, res: Resource, direction: int):
        self.port = Port(res, direction)

    def render_port(self, x0: int, y0: int, screen: pygame.Surface):
        if self.port is None:
            return
        img = pygame.transform.rotozoom(ResourceManager.PORTS[self.port.resource], self.port.direction,
                                        ResourceManager.SCALE_PORTS_IMAGES)
        w, h = img.get_size()
        w, h = w, h

        x1, y1 = self.intersections[0].position(x0, y0)
        x2, y2 = self.intersections[1].position(x0, y0)

        rad = self.port.direction * pi / 180
        x = (x1 + x2 + cos(rad) * ResourceManager.TILE_PATH_LENGTH - w) / 2
        y = (y1 + y2 - sin(rad) * ResourceManager.TILE_PATH_LENGTH - h) / 2

        screen.blit(img, (x, y))

    def render_first_layer(self, x0: int, y0: int, screen: pygame.Surface):
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        if self.road_player is None:
            pygame.draw.aaline(screen, (0, 0, 0), start, end, 1)
        else:
            pygame.draw.line(screen, (0, 0, 0), start, end, ResourceManager.ROAD_WIDTH + 2)
            pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                         ResourceManager.ROAD_WIDTH // 2, (0, 0, 0))
            pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                         ResourceManager.ROAD_WIDTH // 2, (0, 0, 0))

    def render_second_layer(self, x0: int, y0: int, screen: pygame.Surface):
        if self.road_player is None:
            return
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        pygame.draw.line(screen, self.road_player.color.value, start, end, ResourceManager.ROAD_WIDTH - 2)
        pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road_player.color.value)
        pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road_player.color.value)
