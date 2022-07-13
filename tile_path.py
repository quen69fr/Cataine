from __future__ import annotations

import pygame.gfxdraw

from color import COLOR_ROAD_EDGES, Color
# from player import Player
from resource_manager import ResourceManager
from tile_intersection import TileIntersection


class TilePath:
    def __init__(self, intersections: list[TileIntersection]):
        self.intersections = intersections
        self.road_player: 'Player' | None = None
        self.port = None  # TODO

    def render_first_layer(self, x0: int, y0: int, screen: pygame.Surface):
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        if self.road_player is None:
            pygame.draw.aaline(screen, COLOR_ROAD_EDGES, start, end, 1)
        else:
            pygame.draw.line(screen, COLOR_ROAD_EDGES, start, end, ResourceManager.ROAD_WIDTH + 2)
            pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                         ResourceManager.ROAD_WIDTH // 2, COLOR_ROAD_EDGES)
            pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                         ResourceManager.ROAD_WIDTH // 2, COLOR_ROAD_EDGES)

    def render_second_layer(self, x0: int, y0: int, screen: pygame.Surface):
        if self.road_player is None:
            return
        start = self.intersections[0].position(x0, y0)
        end = self.intersections[1].position(x0, y0)
        pygame.draw.line(screen, self.road_player.value, start, end, ResourceManager.ROAD_WIDTH - 2)
        pygame.gfxdraw.filled_circle(screen, int(start[0]), int(start[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road_player.color.value)
        pygame.gfxdraw.filled_circle(screen, int(end[0]), int(end[1]),
                                     ResourceManager.ROAD_WIDTH // 2 - 2, self.road_player.color.value)
