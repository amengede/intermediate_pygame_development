from config import *
import adventure_view
import combat_view
import model

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
    
    def run(self) -> None:

        self.game_context = model.game_context["adventure"]
        self.game_context.load_from_file("levels/forest.txt")
        self.adventure_mainloop()
    
    def transition_into_battle(self) -> None:

        self.renderer_context.save_screen()
        t = 0
        SFX["battle_alert"].play()
        while t < 60:
            self.renderer_context.render_saved_screen(t / 60)
            t += 1
            self.clock.tick(60)

        self.game_context = model.game_context["combat"]
        self.game_context.reset_state()
        self.game_context.load_from_file("battle_data.txt")
        self.combat_mainloop()
    
    def transition_into_adventure(self) -> None:

        self.game_context = model.game_context["adventure"]
        self.game_context.reset_party_state()
        self.game_context.load_from_file("party_data.txt")
        self.adventure_mainloop()

    def adventure_mainloop(self):

        self.renderer_context = adventure_view.renderer_context
        self.game_context = model.game_context["adventure"]
        MUSIC["adventure"].play()

        return_action = model.RETURN_ACTION_CONTINUE
        while return_action == model.RETURN_ACTION_CONTINUE:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return_action = model.RETURN_ACTION_GAME_END
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    if self.game_context.mode == MODE_WALKING:
                        self.game_context.make_player_interact()
                    else:
                        self.game_context.mode = MODE_WALKING
            
            if return_action == model.RETURN_ACTION_GAME_END:
                break
            
            if self.game_context.mode == MODE_WALKING:
                self.handle_keys_adventure()
                return_action = self.game_context.update()
                line = ""
            else:
                line = self.game_context.line

            self.renderer_context.draw(
                terrain = self.game_context.terrain,
                player = self.game_context.player,
                villagers = self.game_context.villagers,
                line = line
            )
            
            self.clock.tick(60)

        MUSIC["adventure"].stop()
        if return_action == model.RETURN_ACTION_START_BATTLE:
            self.transition_into_battle()

    def combat_mainloop(self):

        self.renderer_context = combat_view.renderer_context
        self.game_context = model.game_context["combat"]
        MUSIC["combat"].play()

        return_action = model.RETURN_ACTION_CONTINUE
        while return_action == model.RETURN_ACTION_CONTINUE:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return_action = model.RETURN_ACTION_GAME_END
                
                if event.type == pg.KEYDOWN:
                    self.game_context.handle_keypress(event)
            
            if return_action == model.RETURN_ACTION_GAME_END:
                break
            
            return_action = self.game_context.update()

            self.renderer_context.draw()
            
            self.clock.tick(60)
        
        MUSIC["combat"].stop()
        if return_action == model.RETURN_ACTION_RETURN_TO_ADVENTURE:
            self.transition_into_adventure()