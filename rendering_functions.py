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


def render_button(screen: pygame.Surface, x: int, y: int, width: int, height: int, text: str, size_text: int,
                  selected: bool = False, unselectable: bool = False):
    if selected:
        color_bounds = (0, 0, 0)
        color_inside = (190, 190, 190)
        color_text = (0, 0, 0)
    elif unselectable:
        color_bounds = (190, 190, 190)
        color_inside = (190, 190, 190)
        color_text = (0, 0, 0)
    else:
        color_bounds = (0, 0, 0)
        color_inside = (0, 0, 0)
        color_text = (190, 190, 190)
    screen.fill(color_bounds, (x, y, width, height))
    screen.fill(color_inside, (x + 3, y + 3, width - 6, height - 6))
    render_text(screen, text, x + width // 2, y + height // 2, size_text, color_text)


def render_rectangle(screen: pygame.Surface, x: int, y: int, width: int, height: int, left_arrow: bool = False,
                     bottom_arrow: bool = False):
    screen.fill((0, 0, 0), (x, y, width, height))
    screen.fill((255, 255, 255), (x + 3, y + 3, width - 6, height - 6))
    if left_arrow:
        ps = [(x - 8, y + height // 2), (x, y + height // 2 - 8), (x, y + height // 2 + 8)]
        pygame.draw.polygon(screen, (0, 0, 0), ps)
        pygame.draw.polygon(screen, (255, 255, 255), [(a + 4, b) for a, b in ps])
    if bottom_arrow:
        ps = [(x + width // 2, y + height + 8), (x + width // 2 - 8, y + height), (x + width // 2 + 8, y + height)]
        pygame.draw.polygon(screen, (0, 0, 0), ps)
        pygame.draw.polygon(screen, (255, 255, 255), [(a, b - 4) for a, b in ps])
