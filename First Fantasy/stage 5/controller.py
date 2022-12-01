from config import *
import adventure_model
import adventure_view
import combat_model
import combat_view

class App:


    def __init__(self):

        pg.init()
        self.clock = pg.time.Clock()
    
    def handle_keys_adventure(self) -> None:

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
        self.game_context.move_player(movement)
    
    def run(self):

        self.combat_mainloop()

    def adventure_mainloop(self):

        self.renderer_context = adventure_view.renderer_context
        self.game_context = adventure_model.game_context
        self.game_context.load_from_file("levels/forest.txt")

        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    if self.game_context.get_mode() == adventure_model.MODE_WALKING:
                        self.game_context.make_player_interact()
                    else:
                        self.game_context.set_mode(adventure_model.MODE_WALKING)
            
            if self.game_context.get_mode() == adventure_model.MODE_WALKING:
                self.handle_keys_adventure()
                self.game_context.update()
                line = ""
            else:
                line = self.game_context.get_line()

            self.renderer_context.draw(
                terrain = self.game_context.get_terrain(),
                player = self.game_context.get_player(),
                villagers = self.game_context.get_villagers(),
                line = line
            )
            
            self.clock.tick(60)

    def combat_mainloop(self):

        self.renderer_context = combat_view.renderer_context
        self.game_context = combat_model.game_context
        self.game_context.load_from_file("battle_data.txt")

        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                
                if event.type == pg.KEYDOWN:
                    self.game_context.handle_keypress(event)
            
            self.game_context.update()

            self.renderer_context.draw(self.game_context)
            
            self.clock.tick(60)