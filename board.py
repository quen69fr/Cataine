from __future__ import annotations

import pygame
from random import shuffle
from typing import TYPE_CHECKING

from resource import Resource, BOARD_PORT_INDEXES_PATHS, BOARD_PORT_DIRECTION
from dev_cards import DevCard, NUM_DEV_CARDS
from resource_manager import ResourceManager
from constants import LIST_TILES_COORDS, LIST_TILES_INTERSECTIONS_COORDS, THIEF_INITIAL_TILE, SIZE_MIN_LARGEST_ARMY
from tile import Tile
from tile_intersection import TileIntersection
from tile_path import TilePath

if TYPE_CHECKING:
    from player import Player


class Board:
    def __init__(self, list_tiles_resources: list[Resource], list_tiles_dice_numbers: list[int],
                 list_ports_resources: list[Resource]):
        self.tiles: list[Tile] = []
        self.paths: list[TilePath] = []
        self.intersections: list[TileIntersection] = []

        self.create_bord(list_tiles_resources, list_tiles_dice_numbers, list_ports_resources)

        self.thief_tile: Tile = self.tiles[THIEF_INITIAL_TILE]

        self.dev_cards: list[DevCard] = sum([[card for _ in range(num)] for card, num in NUM_DEV_CARDS.items()],
                                            start=[])
        shuffle(self.dev_cards)

        self.players_longest_road: list[Player] = []
        self.player_largest_army: Player | None = None

    def update_longest_road(self, player: 'Player'):
        lr = self.players_longest_road
        bonus = 1 if player == self.players_longest_road[0] else 0
        self.players_longest_road = []
        added = False
        for p in lr:
            if p == player:
                continue
            if not added and p.length_longest_road < player.length_longest_road + bonus:
                self.players_longest_road.append(player)
                added = True
            self.players_longest_road.append(p)
        if not added:
            self.players_longest_road.append(player)

    def create_bord(self, list_tiles_resources: list[Resource], list_tiles_dice_numbers: list[int],
                    list_ports_resources: list[Resource]):
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
        for index, resource, direction in zip(BOARD_PORT_INDEXES_PATHS, list_ports_resources, BOARD_PORT_DIRECTION):
            self.paths[index].add_port(resource, direction)

    def mouse_on_intersection(self, x0: int, y0: int, x_mouse: int, y_mouse: int) -> TileIntersection | None:
        for inter in self.intersections:
            x, y = inter.position(x0, y0)
            if (x - x_mouse) ** 2 + (y - y_mouse) ** 2 <= ResourceManager.TILE_PATH_LENGTH ** 2 / 4:
                return inter
        return None

    def mouse_on_tile(self, x0: int, y0: int, x_mouse: int, y_mouse: int) -> Tile | None:
        for tile in self.tiles:
            x, y = tile.position(x0, y0)
            if (x + ResourceManager.TILE_WIDTH // 2 - x_mouse) ** 2 + \
                    (y + ResourceManager.TILE_HEIGHT // 2 - y_mouse) ** 2 <= ResourceManager.TILE_WIDTH ** 2 / 4:
                return tile
        return None

    def mouse_on_path(self, x0: int, y0: int, x_mouse: int, y_mouse: int) -> TilePath | None:
        for path in self.paths:
            x1, y1 = path.intersections[0].position(x0, y0)
            x2, y2 = path.intersections[1].position(x0, y0)
            if (x1 + x2 - 2 * x_mouse) ** 2 + (y1 + y2 - 2 * y_mouse) ** 2 <= ResourceManager.TILE_WIDTH ** 2 / 4:
                return path
        return None

    def render(self, x0: int, y0: int, screen: pygame.Surface):
        for tile in self.tiles:
            tile.render(x0, y0, screen, tile == self.thief_tile)
        for path in self.paths:
            path.render_port(x0, y0, screen)
            path.render_first_layer(x0, y0, screen)
        for path in self.paths:
            path.render_second_layer(x0, y0, screen)
        for intersection in self.intersections:
            intersection.render(x0, y0, screen)
