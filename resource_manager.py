from __future__ import annotations

import pygame

from color import Color
from construction import ConstructionKind
from rendering_functions import render_text, render_road
from resource import Resource
from dev_cards import DevCard


class ResourceManager:
    BACKGROUND: pygame.Surface = None

    CARDS_RESOURCES_AND_DEV: dict[Resource | DevCard, pygame.Surface] = {}
    BACK_CARD: pygame.Surface = None
    CARD_WIDTH, CARD_HEIGHT = 0, 0

    TILES: dict[Resource, pygame.Surface] = {}
    CONSTRUCTIONS: dict[ConstructionKind, dict[Color, pygame.Surface]] = {
        ConstructionKind.ROAD: {},
        ConstructionKind.COLONY: {},
        ConstructionKind.TOWN: {}
    }

    TILE_WIDTH, TILE_HEIGHT = 0, 0
    TILE_HAT_HEIGHT = 38
    TILE_PATH_LENGTH = 76
    ROAD_WIDTH = 12

    THIEF_IMAGE = None
    THIEF_IMAGE_WITH_DICE_NUMBER = None

    DICE_NUMBER_RADIUS = 20
    DICE_NUMBER_IMAGE: dict[int, pygame.Surface] = {}

    PORTS: dict[Resource, pygame.Surface] = {}
    SCALE_PORTS_IMAGES = 0.9

    PLAYER_LOGO: pygame.Surface = None
    CROWN: pygame.Surface = None
    SMALL_CROWN: pygame.Surface = None
    SMALL_CROWN_GRAY: pygame.Surface = None
    SMALL_KNIGHT_CARD: pygame.Surface = None
    SMALL_DEV_CARD: pygame.Surface = None

    @staticmethod
    def load():
        ResourceManager.BACKGROUND = pygame.image.load("images/FondEau.png")

        ResourceManager.CARDS_RESOURCES_AND_DEV[Resource.WOOL] = pygame.image.load("images/CarteMouton.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[Resource.ROCK] = pygame.image.load("images/CartePierre.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[Resource.HAY] = pygame.image.load("images/CarteFoin.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[Resource.CLAY] = pygame.image.load("images/CarteArgile.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[Resource.WOOD] = pygame.image.load("images/CarteBois.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[DevCard.KNIGHT] = pygame.image.load("images/CarteChevalier.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[DevCard.FREE_CARDS] = \
            pygame.image.load("images/CarteRessourcesGratuites.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[DevCard.MONOPOLY] = pygame.image.load("images/CarteMonopole.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[DevCard.FREE_ROADS] = \
            pygame.image.load("images/CarteRoutesGratuites.png")
        ResourceManager.CARDS_RESOURCES_AND_DEV[DevCard.VICTORY_POINT] = \
            pygame.image.load("images/CartePointVictoire.png")
        ResourceManager.BACK_CARD = pygame.image.load("images/CarteDos.png")
        ResourceManager.CARD_WIDTH, ResourceManager.CARD_HEIGHT = ResourceManager.BACK_CARD.get_size()

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
            # Colony
            colored_colony = pygame.Surface(colony.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(colored_colony, color.value, [(3, 9), (15, 1), (26, 9), (26, 25), (3, 25)], 0)
            colored_colony.blit(colony, (0, 0))
            ResourceManager.CONSTRUCTIONS[ConstructionKind.COLONY][color] = colored_colony

            # Town
            colored_town = pygame.Surface(town.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(colored_town, color.value, [(3, 9), (19, 1), (34, 9), (34, 33), (3, 33)], 0)
            colored_town.blit(town, (0, 0))
            ResourceManager.CONSTRUCTIONS[ConstructionKind.TOWN][color] = colored_town

            # Road
            road = pygame.Surface((55, 30))
            road.fill((255, 255, 255))
            render_road(road, (48, 8), (8, 21), ResourceManager.ROAD_WIDTH, color.value)
            ResourceManager.CONSTRUCTIONS[ConstructionKind.ROAD][color] = road

        # make the circles around the dice numbers
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

        ResourceManager.PORTS[Resource.ROCK] = pygame.image.load("images/PortPierre.png")
        ResourceManager.PORTS[Resource.WOOD] = pygame.image.load("images/PortBois.png")
        ResourceManager.PORTS[Resource.HAY] = pygame.image.load("images/PortFoin.png")
        ResourceManager.PORTS[Resource.CLAY] = pygame.image.load("images/PortArgile.png")
        ResourceManager.PORTS[Resource.WOOL] = pygame.image.load("images/PortMouton.png")
        ResourceManager.PORTS[Resource.P_3_FOR_1] = pygame.image.load("images/Port3contre1.png")

        ResourceManager.PLAYER_LOGO = pygame.image.load("images/Joueur.png")
        ResourceManager.CROWN = pygame.image.load("images/Couronne.png")
        ResourceManager.SMALL_CROWN = pygame.image.load("images/PetiteCouronneDoree.png")
        ResourceManager.SMALL_CROWN_GRAY = pygame.image.load("images/PetiteCouronneGrisee.png")

        ResourceManager.SMALL_KNIGHT_CARD = pygame.image.load("images/PetiteCarteChevalier.png")
        ResourceManager.SMALL_DEV_CARD = pygame.image.load("images/CarteDosSpeciale.png")
