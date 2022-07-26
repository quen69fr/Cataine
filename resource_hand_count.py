from __future__ import annotations

from typing import Generator
from random import randint
from resource import Resource, ORDER_RESOURCES


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

    def add_one(self, res: Resource, num: int = 1):
        self[res] += num

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

    def num_resources(self):
        return sum(self.values())

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

    def subsets_of_size_k(self, k: int) -> Generator[ResourceHandCount]:
        for subset in self.subsets():
            if sum(subset.values()) == k:
                yield subset

    def random_resource(self):
        assert sum(self.values()) > 0
        n = randint(0, sum(self.values()) - 1)
        for res in ORDER_RESOURCES:
            n -= self[res]
            if n < 0:
                return res
        assert False

    def list_resources(self) -> Generator[Resource]:
        for res in ORDER_RESOURCES:
            for _ in range(self[res]):
                yield res

    def __iter__(self):
        return self.items().__iter__()
