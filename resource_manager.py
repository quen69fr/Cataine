from __future__ import annotations

import pygame.gfxdraw

from render_text import render_text
from resource import Resource
from construction import Construction
from color import Color


class ResourceManager:
    TILES: dict[Resource, pygame.Surface] = {}
    CONSTRUCTIONS: dict[Construction, dict[Color, pygame.Surface]] = {
        Construction.COLONY: {},
        Construction.TOWN: {}
    }

    TILE_WIDTH, TILE_HEIGHT = 0, 0
    TILE_HAT_HEIGHT = 38
    ROAD_WIDTH = 12

    THIEF_IMAGE = None
    THIEF_IMAGE_WITH_DICE_NUMBER = None

    DICE_NUMBER_RADIUS = 20
    DICE_NUMBER_IMAGE: dict[int, pygame.Surface] = {}

    @staticmethod
    def load():
        ResourceManager.TILES[Resource.WOOL] = pygame.image.load("images/TuileMouton.png")
        ResourceManager.TILES[Resource.ROCK] = pygame.image.load("images/TuilePierre.png")
        ResourceManager.TILES[Resource.DESERT] = pygame.image.load("images/TuileDesert.png")
        ResourceManager.TILES[Resource.HAY] = pygame.image.load("images/TuileFoin.png")
        ResourceManager.TILES[Resource.CLAY] = pygame.image.load("images/TuileArgile.png")
        ResourceManager.TILES[Resource.WOOD] = pygame.image.load("images/TuileBois.png")

        ResourceManager.TILE_WIDTH, ResourceManager.TILE_HEIGHT = ResourceManager.TILES[Resource.DESERT].get_size()

        colony = pygame.image.load("images/Colonie.png")
        town = pygame.image.load("images/Ville.png")
        # We display the color of the construction and then blit the black image above
        for color in Color:
            colored_colony = pygame.Surface(colony.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(colored_colony, color.value, [(3, 9), (15, 1), (26, 9), (26, 25), (3, 25)], 0)
            colored_colony.blit(colony, (0, 0))
            ResourceManager.CONSTRUCTIONS[Construction.COLONY][color] = colored_colony

            colored_town = pygame.Surface(town.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(colored_town, color.value, [(3, 9), (19, 1), (34, 9), (34, 33), (3, 33)], 0)
            colored_town.blit(town, (0, 0))
            ResourceManager.CONSTRUCTIONS[Construction.TOWN][color] = colored_town

        r = ResourceManager.DICE_NUMBER_RADIUS
        for num in range(2, 13):
            img_num = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
            pygame.draw.circle(img_num, (255, 255, 255), (r, r), r, 0)
            pygame.gfxdraw.aacircle(img_num, r, r, r, (0, 0, 0))
            pygame.gfxdraw.aacircle(img_num, r, r, r - 2, (0, 0, 0))
            c = (0, 0, 0)
            size = 35
            if num == 6 or num == 8:
                c = (225, 0, 0)
                size += 10
            elif num == 5 or num == 9:
                size += 10
            elif num == 11 or num == 3:
                size -= 5
            elif num == 12 or num == 2:
                size -= 10

            render_text(img_num, str(num), r, r + 2, size, c)

            ResourceManager.DICE_NUMBER_IMAGE[num] = img_num

        ResourceManager.THIEF_IMAGE = pygame.image.load("images/Voleur.png")
        ResourceManager.THIEF_IMAGE_WITH_DICE_NUMBER = pygame.image.load("images/VoleurNumero.png")
