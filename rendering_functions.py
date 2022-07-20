from __future__ import annotations

import pygame


fonts = {}


def render_text(screen: pygame.Surface, text: str, x: int | float, y: int | float, size: int, couleur: tuple = None,
                centred: bool = True, font=None):
    if (font, size) not in fonts:
        fonts[(font, size)] = pygame.font.Font(font, int(size))
    if couleur is None:
        couleur = (0, 0, 0)
    surface = fonts[(font, size)].render(text, True, couleur)
    rect = surface.get_rect(topleft=(x, y))
    if centred:
        rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
