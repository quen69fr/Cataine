from __future__ import annotations

from resource import Resource

import pygame


class ResourceManager:

    TILES: dict[Resource, pygame.Surface] = {}

    @staticmethod
    def load():
        ResourceManager.TILES[Resource.WOOL] = pygame.image.load("images/TuileMouton.png")
        ResourceManager.TILES[Resource.ROCK] = pygame.image.load("images/TuilePierre.png")
        ResourceManager.TILES[Resource.DESERT] = pygame.image.load("images/TuileDesert.png")
        ResourceManager.TILES[Resource.HAY] = pygame.image.load("images/TuileFoin.png")
        ResourceManager.TILES[Resource.CLAY] = pygame.image.load("images/TuileArgile.png")
        ResourceManager.TILES[Resource.WOOD] = pygame.image.load("images/TuileBois.png")


