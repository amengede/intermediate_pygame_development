import pygame as pg

SCREEN_SIZE = (640, 480)
BG_COLOR = (32, 128, 192)

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        screen_surface.fill(BG_COLOR)
        
        pg.display.flip()

if __name__ == "__main__":
    main()