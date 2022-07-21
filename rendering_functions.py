from __future__ import annotations

import pygame.gfxdraw


fonts = {}


def render_text(screen: pygame.Surface, text: str, x: int | float, y: int | float, size: int,
                color: tuple[int, int, int] = None,
                centred: bool = True, font=None):
    if (font, size) not in fonts:
        fonts[(font, size)] = pygame.font.Font(font, int(size))
    if color is None:
        color = (0, 0, 0)
    surface = fonts[(font, size)].render(text, True, color)
    rect = surface.get_rect(topleft=(x, y))
    if centred:
        rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def alpha_image(image: pygame.Surface, alpha_value: int):
    tmp = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tmp.fill((255, 255, 255, alpha_value))
    image = image.copy()
    image.blit(tmp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return image


def render_road(screen: pygame.Surface, p1: tuple[int, int], p2: tuple[int, int], road_width: int,
                color: tuple[int, int, int]):
    pygame.draw.line(screen, (0, 0, 0), p1, p2, road_width + 2 - 1)
    pygame.gfxdraw.filled_circle(screen, p1[0], p1[1], road_width // 2, (0, 0, 0))
    pygame.gfxdraw.filled_circle(screen, p2[0], p2[1], road_width // 2, (0, 0, 0))
    pygame.draw.line(screen, color, p1, p2, road_width - 2 - 1)
    pygame.gfxdraw.filled_circle(screen, p1[0], p1[1], road_width // 2 - 2, color)
    pygame.gfxdraw.filled_circle(screen, p2[0], p2[1], road_width // 2 - 2, color)

