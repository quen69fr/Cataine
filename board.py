from __future__ import annotations

import pygame

from constants import *
from resource import Resource
from tile import Tile
from tile_path import TilePath
from tile_intersection import TileIntersection


class Board:
    def __init__(self, list_tiles_resources: list[Resource], list_tiles_dice_numbers: list[int]):
        self.tiles = []
        self.paths = []
        self.intersections = []

        self.create_bord(list_tiles_resources, list_tiles_dice_numbers)

    def create_bord(self, list_tiles_resources: list[Resource], list_tiles_dice_numbers: list[int]):
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

        for (i, j), res, num in zip(LIST_TILES_COORDS, list_tiles_resources, list_tiles_dice_numbers):
            tile = Tile(res, i, j, num)
            self.tiles.append(tile)
            first_inter = None
            first_inter_exists = True
            previous_inter = None
            previous_inter_exists = False
            for di, dj in LIST_TILES_INTERSECTIONS_COORDS:
                inter = find_intersection(i + di, j + dj)
                inter_exists = inter is not None
                if not inter_exists:
                    inter = TileIntersection(i + di, j + dj)
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
