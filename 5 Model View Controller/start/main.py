from config import *
import classes

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()

    game_context = classes.game_context

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                game_context.reset_state()
                game_context.load_random_state()
        
        game_context.update()

        screen_surface.fill(BG_COLOR)
        game_context.draw(screen_surface)
        
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()