from config import *
import model
import view

renderer_context = view.renderer_context
game_context = model.game_context

class App:


    def __init__(self):

        pg.init()
        self.clock = pg.time.Clock()
        game_context.load_from_file("levels/forest.txt")
    
    def handle_keys(self) -> None:

        keys_pressed = pg.key.get_pressed()

        movement = [0,0]
        if keys_pressed[pg.K_LEFT]:
            movement[0] -= 1
        if keys_pressed[pg.K_RIGHT]:
            movement[0] += 1
        if keys_pressed[pg.K_UP]:
            movement[1] -= 1
        if keys_pressed[pg.K_DOWN]:
            movement[1] += 1
        game_context.move_player(movement)

    def run(self):

        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    if game_context.get_mode() == model.MODE_WALKING:
                        game_context.make_player_interact()
                    else:
                        game_context.set_mode(model.MODE_WALKING)
            
            if game_context.get_mode() == model.MODE_WALKING:
                self.handle_keys()
                game_context.update()
                line = ""
            else:
                line = game_context.get_line()

            renderer_context.draw(
                terrain = game_context.get_terrain(),
                player = game_context.get_player(),
                villagers = game_context.get_villagers(),
                line = line
            )
            
            self.clock.tick(60)