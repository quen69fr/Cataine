
import pygame

from constants import *
from tile import Tile
from tile_path import TilePath
from tile_intersection import TileIntersection


class Board:
    def __init__(self):
        self.tiles = []
        self.paths = []
        self.intersections = []

    def create_bord(self, list_tiles_resources: list[int], list_tiles_dice_number):
        def find_intersection(x, y):
            for intersection in self.intersections:
                if (intersection.x, intersection.y) == (x, y):
                    return intersection
            return None

        def create_path(inter1, inter2):
            path = TilePath([inter1, inter2])
            inter1.add_neighbour_path(path)
            inter2.add_neighbour_path(path)
            return path

        n = len(LIST_TILES_INTERSECTIONS_COORDS)
        for (i, j), res, num in zip(LIST_TILES_COORDS, list_tiles_resources, list_tiles_dice_number):
            tile = Tile(res, i, j, num)
            self.tiles.append(tile)
            first_inter = None
            first_inter_exists = True
            previous_inter = None
            previous_inter_exists = False
            for d in range(n):
                di, dj = LIST_TILES_INTERSECTIONS_COORDS[d]
                inter = find_intersection(i + di, j + dj)
                inter_exists = inter is None
                if not inter_exists:
                    inter = TileIntersection()
                    self.intersections.append(inter)
                    if first_inter is None:
                        first_inter_exists = False
                inter.add_neighbour_tile(tile)
                if first_inter is None:
                    first_inter = inter
                if previous_inter is not None and not (inter_exists or previous_inter_exists):
                    create_path(inter, previous_inter)
                tile.add_intersection(inter)
                previous_inter = inter
                previous_inter_exists = inter_exists
            if not (previous_inter_exists and first_inter_exists):
                self.paths.append(create_path(first_inter, previous_inter))

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        for tile in self.tiles:
            tile.render(x0, y0, screen)
        for path in self.paths:
            path.render(x0, y0, screen)
        for intersection in self.intersections:
            intersection.render(x0, y0, screen)
