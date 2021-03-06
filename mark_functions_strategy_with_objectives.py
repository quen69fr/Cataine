
from __future__ import annotations

from typing import TYPE_CHECKING
from tile_intersection import TileIntersection
from tile import Tile
from probability import get_probability_to_roll
from resource import Resource
from resource_hand_count import ResourceHandCount
from construction import ConstructionKind

if TYPE_CHECKING:
    from player import Player


def mark_objective(player: Player, cost_no_modify: ResourceHandCount, initial_gain: float) -> float:
    # TODO : Take into account the number of cards for the thief
    #  -> Maybe with 2 objectives in parallel (recursion ?)...
    cost = cost_no_modify.copy()
    required_cards = cost.copy()

    # breakpoint()

    # TODO : We could be more precise with the ports...
    prod_turns = player.get_resource_production_in_number_of_turns_with_systematic_exchange(with_thief=True)
    cost.subtract_fine_if_not_present(player.resource_cards)
    cost_num_turns = max(num * prod_turns[res] for res, num in cost.items())

    # build list of required cards - current hand
    # max of the inverse probabilities for each card = number of turns to be able to complete the objective = n
    # after n turns, estimate our hand = hand', do hand' - required cards
    # convert that into a number

    # add cards in the current hand
    hand_after_cost_num_turns: dict[Resource, float] = {}
    for res, count in player.resource_cards.items():
        hand_after_cost_num_turns[res] = count

    # predict cards and add to future hands
    for res, expectation in player.get_resource_production_expectation_with_thief().items():
        hand_after_cost_num_turns[res] += expectation * cost_num_turns

    # remove all resources that will be used by this objective
    for res, count in required_cards.items():
        hand_after_cost_num_turns[res] -= count
        # assert hand_after_cost_num_turns[res] >= 0

    gain = 150 * initial_gain
    for res, count in hand_after_cost_num_turns.items():
        gain += count * prod_turns[res] * mark_resource(player, res)
    gain += 100
    gain = max(gain, 0)
    return gain ** 2 / (cost_num_turns + 1)


def mark_resource(player: Player, resource: Resource):
    if resource == Resource.DESERT:
        return 0
    ports = list(player.get_ports())
    c = 80
    if resource in ports:
        c = 40
    elif Resource.P_3_FOR_1 in ports:
        c = 60
    return (1 if Resource.P_3_FOR_1 in ports else 0.95) / \
           ((1 + c * player.production_expectation[resource]) ** 0.6)


def mark_port(player: Player, resource: Resource, special_expectation: float = None):
    expectation = special_expectation
    if resource == Resource.P_3_FOR_1:
        if expectation is None:
            expectation = max(player.production_expectation.values())
        return 0.6 * expectation / 3
    else:
        if expectation is None:
            expectation = player.production_expectation[resource]
        return 0.7 * expectation / 2


def mark_resource_expectation(player: Player, resource: Resource, expectation: float):
    mark = expectation * mark_resource(player, resource)
    if resource in player.get_ports():
        mark += mark_port(player, resource, special_expectation=expectation)
    return mark


def mark_intersection(player: Player, intersection: TileIntersection):
    ports = list(player.get_ports())
    mark = 0
    for tile in intersection.neighbour_tiles:
        if tile.resource == Resource.DESERT:
            continue
        expectation = get_probability_to_roll(tile.dice_number)
        mark += mark_resource_expectation(player, tile.resource, expectation)
    for path in intersection.neighbour_paths:
        if path.port is not None and path.port.resource not in ports:
            if path.port.resource == Resource.P_3_FOR_1:
                mark += mark_port(player, path.port.resource)
            else:
                special_expectation = player.production_expectation[path.port.resource]
                for tile in intersection.neighbour_tiles:
                    if tile.resource == path.port.resource:
                        special_expectation += get_probability_to_roll(tile.dice_number)
                mark += mark_port(player, path.port.resource, special_expectation=special_expectation)
    return 6 * mark


def mark_tile_thief(player: Player, tile: Tile):
    has_someone_to_steal = False
    mark = 0
    for inter in tile.intersections:
        if inter.content is not None:
            c = 1 if inter.content.kind == ConstructionKind.COLONY else 2
            coef = 1
            if inter.content.player == player:
                coef = -5
            else:
                if not inter.content.player.num_resources() == 0:
                    has_someone_to_steal = True
            mark += c * coef * mark_resource(inter.content.player, tile.resource)
    if tile.resource == Resource.DESERT:
        mark = 0
    else:
        mark *= get_probability_to_roll(tile.dice_number)
    if has_someone_to_steal:
        mark += 1
    return mark
