from __future__ import annotations

import pygame


def render_text(screen: pygame.Surface, text: str, x: int | float, y: int | float, size: int, couleur: tuple,
                centred: bool = True, font=None):
    pygame_font = pygame.font.Font(font, int(size))
    surface = pygame_font.render(text, True, couleur)
    rect = surface.get_rect(topleft=(x, y))
    if centred:
        rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
