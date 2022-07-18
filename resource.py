from __future__ import annotations

from typing import Generator
from enum import Enum
from dataclasses import dataclass


class Resource(Enum):
    DESERT = 0
    CLAY = 1
    WOOL = 2
    HAY = 3
    ROCK = 4
    WOOD = 5
    P_3_FOR_1 = 6


class ResourceHandCount(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Resource.CLAY not in self:
            self[Resource.CLAY] = 0
        if Resource.WOOD not in self:
            self[Resource.WOOD] = 0
        if Resource.WOOL not in self:
            self[Resource.WOOL] = 0
        if Resource.HAY not in self:
            self[Resource.HAY] = 0
        if Resource.ROCK not in self:
            self[Resource.ROCK] = 0

    def add_one(self, res: Resource):
        self[res] += 1

    def try_consume_one(self, res: Resource):
        if self[res] >= 1:
            self[res] -= 1
            return True
        return False

    def has(self, cost: ResourceHandCount):
        for res, count in cost.items():
            if self[res] < count:
                return False
        return True

    def consume(self, cost: ResourceHandCount):
        for res, count in cost.items():
            self[res] -= count
            assert self[res] >= 0

    def add(self, cost: ResourceHandCount):
        for res, count in cost.items():
            self[res] += count

    def subtract_fine_if_not_present(self, cost: ResourceHandCount):
        for res in cost.keys():
            self[res] = max(0, self[res] - cost[res])

    def copy(self) -> ResourceHandCount:
        return ResourceHandCount(self)

    def subsets(self) -> Generator[ResourceHandCount]:
        for res, num in self:
            if num > 0:
                self[res] = 0
                for sub_set in self.subsets():
                    yield sub_set.copy()
                    for _ in range(num):
                        sub_set.add_one(res)
                        yield sub_set.copy()
                return
        yield ResourceHandCount()

    def __iter__(self):
        return self.items().__iter__()


@dataclass
class Port:
    resource: Resource
    direction: int


BOARD_LAYOUT_RESOURCES = [
    Resource.WOOD,
    Resource.WOOL,
    Resource.WOOL,
    Resource.HAY,
    Resource.ROCK,
    Resource.HAY,
    Resource.WOOD,
    Resource.WOOD,
    Resource.CLAY,
    Resource.DESERT,
    Resource.ROCK,
    Resource.HAY,
    Resource.HAY,
    Resource.ROCK,
    Resource.WOOD,
    Resource.WOOL,
    Resource.CLAY,
    Resource.WOOL,
    Resource.CLAY
]
BOARD_LAYOUT_DICE_NUMBERS = [6, 3, 8, 2, 4, 5, 10, 5, 9, 0, 6, 9, 10, 11, 3, 12, 8, 4, 11]

BOARD_PORT_RESOURCES = [
    Resource.P_3_FOR_1,
    Resource.WOOL,
    Resource.ROCK,
    Resource.P_3_FOR_1,
    Resource.P_3_FOR_1,
    Resource.HAY,
    Resource.CLAY,
    Resource.P_3_FOR_1,
    Resource.WOOD
]
BOARD_PORT_INDEXES_PATHS = [5, 6, 19, 27, 46, 52, 60, 64, 67]
BOARD_PORT_DIRECTION = [120, 60, -180, 60, 0, -180, -60, -120, -60]  # In degrees
