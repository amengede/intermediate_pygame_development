from config import *
import model
import view

renderer_context = view.renderer_context
game_context = model.game_context

class App:


    def __init__(self):

        pg.init()
        self.clock = pg.time.Clock()
    
    def handle_keys(self) -> None:

        movement_speed = 1
        keys_pressed = pg.key.get_pressed()
        movement = [0,0]

        if keys_pressed[pg.K_LEFT]:
            movement[0] -= movement_speed
        if keys_pressed[pg.K_RIGHT]:
            movement[0] += movement_speed
        if keys_pressed[pg.K_UP]:
            movement[1] -= movement_speed
        if keys_pressed[pg.K_DOWN]:
            movement[1] += movement_speed
        
        game_context.move_player(movement)

    def run(self):

        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    game_context.reset_state()
                    game_context.load_random_state()
            self.handle_keys()

            renderer_context.draw(
                player = game_context.get_player(),
                inactive = game_context.get_inactive_blocks(),
                active = game_context.get_active_blocks()
            )
            
            self.clock.tick(60)