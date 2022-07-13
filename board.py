from __future__ import annotations

from resource import Resource

import pygame

from constants import LIST_TILES_COORDS, LIST_TILES_INTERSECTIONS_COORDS, THIEF_INITIAL_TILE
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath


class Board:
    def __init__(self, list_tiles_resources: list[Resource], list_tiles_dice_numbers: list[int]):
        self.tiles: list[Tile] = []
        self.paths: list[TilePath] = []
        self.intersections: list[TileIntersection] = []

        self.thief_tile: int = THIEF_INITIAL_TILE

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
            self.paths.append(path)

        for (i, j), res, num in zip(LIST_TILES_COORDS, list_tiles_resources, list_tiles_dice_numbers):
            tile = Tile(res, i, j, num)
            self.tiles.append(tile)
            first_inter = None
            first_inter_exists = True
            previous_inter = None
            previous_inter_exists = False
            for di, dj in LIST_TILES_INTERSECTIONS_COORDS:
                assert i + di >= 0
                assert j + dj >= 0
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
                if previous_inter is not None and not (inter_exists and previous_inter_exists):
                    create_path(inter, previous_inter)
                tile.add_intersection(inter)
                previous_inter = inter
                previous_inter_exists = inter_exists
            if not (previous_inter_exists and first_inter_exists):
                create_path(first_inter, previous_inter)

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        for i, tile in enumerate(self.tiles):
            tile.render(x0, y0, screen, i == self.thief_tile)
        for path in self.paths:
            path.render_first_layer(x0, y0, screen)
        for path in self.paths:
            path.render_second_layer(x0, y0, screen)
        for intersection in self.intersections:
            intersection.render(x0, y0, screen)
