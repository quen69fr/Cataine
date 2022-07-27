from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from logs import log
from resource import Resource
from dev_cards import DevCard
from construction import Construction, ConstructionKind, NUM_CONSTRUCTION_MAX
from resource_hand_count import ResourceHandCount

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
        log(f"Action: {self.player} build a road.")
        self.player.add_road(self.path)
        self.player.consume_resources(self.cost)

    def available(self):
        # path is occupied
        if self.path.road_player is not None:
            return False

        if self.player.num_roads_belonging_to_player() >= NUM_CONSTRUCTION_MAX[ConstructionKind.ROAD]:
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
        log(f"Action: {self.player} build a colony.")
        self.player.add_colony(self.intersection)
        self.player.consume_resources(self.cost)

    def available(self):
        if not self.intersection.can_build():
            return False

        if self.player.num_colonies_belonging_to_player() >= NUM_CONSTRUCTION_MAX[ConstructionKind.COLONY]:
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
        log(f"Action: {self.player} build a town.")
        self.player.add_town(self.intersection)
        self.player.consume_resources(self.cost)

    def available(self):
        if self.player.num_towns_belonging_to_player() >= NUM_CONSTRUCTION_MAX[ConstructionKind.TOWN]:
            return False
        return self.intersection.content == Construction(kind=ConstructionKind.COLONY, player=self.player)


@dataclass
class ActionBuyDevCard(Action):
    player: Player
    cost = ResourceHandCount({Resource.ROCK: 1, Resource.HAY: 1, Resource.WOOL: 1})

    def apply(self):
        log(f"Action: {self.player} buy a dev card.")
        assert self.player.board.dev_cards
        self.player.dev_cards.append(self.player.board.dev_cards.pop())
        self.player.num_dev_cards_just_bought += 1
        self.player.consume_resources(self.cost)

    def available(self):
        return len(self.player.board.dev_cards) > 0


@dataclass
class ActionRevealDevCard(Action):
    dev_card: DevCard
    player: Player
    cost = ResourceHandCount({Resource.ROCK: 1, Resource.HAY: 1, Resource.WOOL: 1})

    def apply(self):
        log(f"Action: {self.player} reveal the dev card {self.dev_card}.")
        self.player.reveal_dev_card(self.dev_card)

    def available(self, before_play: bool = False):
        if before_play and not self.dev_card == DevCard.KNIGHT:
            return False
        if self.player.num_dev_cards_just_bought == 0:
            return self.dev_card in self.player.dev_cards
        return self.dev_card in self.player.dev_cards[:-self.player.num_dev_cards_just_bought]
