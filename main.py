import pygame

screen = pygame.display.set_mode((640, 640))
srect = screen.get_rect()

clock = pygame.time.Clock()

def render_board():
    

def main():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        pygame.display.flip()

if __name__ == "__main__":
    main()
    pygame.quit()
