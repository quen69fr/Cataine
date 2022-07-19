from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from resource import Resource
from dev_cards import DevCard
from typing import TYPE_CHECKING
from construction import Construction, ConstructionKind
from resource import ResourceHandCount

if TYPE_CHECKING:
    from player import Player
    from tile_path import TilePath
    from tile_intersection import TileIntersection


class Action:
    cost: ResourceHandCount

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def available(self):
        # Does not care about the cost
        pass


@dataclass
class ActionBuildRoad(Action):
    path: TilePath
    player: Player
    cost = ResourceHandCount({Resource.WOOD: 1, Resource.CLAY: 1})

    def apply(self):
        if self.path.road_player is not None:
            raise ValueError("building road on a tile path that already has a road")
        self.path.road_player = self.player
        self.player.resource_cards.consume(self.cost)

    def undo(self):
        assert self.path.road_player == self.player
        self.path.road_player = None
        self.player.resource_cards.add(self.cost)

    def available(self):
        # path is occupied
        if self.path.road_player is not None:
            return False

        # check if there is one of our colony/town around it
        def has_own_construction(intersection: TileIntersection):
            return intersection.content is not None and intersection.content.player == self.player

        if has_own_construction(self.path.intersections[0]) or \
                has_own_construction(self.path.intersections[1]):
            return True

        # check if there is one of our road around it
        adjacent_paths = self.path.intersections[0].neighbour_paths + self.path.intersections[1].neighbour_paths
        for p in adjacent_paths:
            if p.road_player == self.player:
                return True

        return False


@dataclass
class ActionBuildColony(Action):
    intersection: TileIntersection
    player: Player
    cost = ResourceHandCount({Resource.WOOD: 1, Resource.CLAY: 1, Resource.WOOL: 1, Resource.HAY: 1})

    def apply(self):
        if self.intersection.content is not None:
            raise ValueError("building colony on a tile intersection that already has a colony")
        self.intersection.content = Construction(kind=ConstructionKind.COLONY, player=self.player)
        self.player.resource_cards.consume(self.cost)

    def undo(self):
        assert self.intersection.content == Construction(kind=ConstructionKind.COLONY, player=self.player)
        self.intersection.content = None
        self.player.resource_cards.add(self.cost)

    def available(self):
        if not self.intersection.can_build():
            return False

        # check if there is one of our road around it
        for p in self.intersection.neighbour_paths:
            if p.road_player == self.player:
                return True
        return False


@dataclass
class ActionBuildTown(Action):
    intersection: TileIntersection
    player: Player
    cost = ResourceHandCount({Resource.ROCK: 3, Resource.HAY: 2})

    def apply(self):
        if not self.intersection.content == Construction(kind=ConstructionKind.COLONY, player=self.player):
            raise ValueError("the town must be built on one of our colony")
        self.intersection.content = Construction(kind=ConstructionKind.TOWN, player=self.player)
        self.player.resource_cards.consume(self.cost)

    def undo(self):
        assert self.intersection.content == Construction(kind=ConstructionKind.TOWN, player=self.player)
        self.intersection.content = Construction(kind=ConstructionKind.COLONY, player=self.player)
        self.player.resource_cards.add(self.cost)

    def available(self):
        return self.intersection.content == Construction(kind=ConstructionKind.COLONY, player=self.player)


@dataclass
class ActionBuyDevCard(Action):
    player: Player
    cost = ResourceHandCount({Resource.ROCK: 1, Resource.HAY: 1, Resource.WOOL: 1})

    def apply(self):
        assert self.player.board.dev_cards
        self.player.dev_cards.insert(0, self.player.board.dev_cards.pop())

    def undo(self):
        assert self.player.dev_cards
        self.player.board.dev_cards.insert(0, self.player.dev_cards.pop())

    def available(self):
        return len(self.player.board.dev_cards) > 0


@dataclass
class ActionRevealDevCard(Action):
    dev_card: DevCard
    player: Player
    cost = ResourceHandCount({Resource.ROCK: 1, Resource.HAY: 1, Resource.WOOL: 1})

    def apply(self):
        pass  # TODO

    def undo(self):
        pass  # TODO

    def available(self):
        return True  # TODO : We can't reveal a dev card that we've just bought
