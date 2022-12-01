from config import *
import model

BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0,0,255)
BG_HIGHLIGHT_COLOR = (64, 160, 224)
TEXT_PANEL_COLOR = BG_HIGHLIGHT_COLOR
PLAYER_COLOR = (128, 32, 128)
BUTTON_INACTIVE_COLOR = (128, 128, 128)
BUTTON_ACTIVE_COLOR = (128, 192, 255)
BUTTON_TEXT_COLOR = (32, 32, 32)

CHARACTER_COLORS = {
    model.SOLDIER: (0, 0, 128),
    model.MAGE: (0, 128, 0),
    model.RAT: (128, 0, 0),
    model.CULTIST: (128, 0, 128)
}

TERRAIN_COLORS = {
    "sky": BG_HIGHLIGHT_COLOR,
    "ground": (69, 39, 2)
}

SCREEN_TEXT_SIZE = 16
SCREEN_TEXT_COLOR = BLACK

environment: model.CombatGameLogic = model.game_context["combat"]

class MapView(pg.sprite.Sprite):

    def __init__(
        self, 
        rect: pg.Rect,
        images: dict[int,pg.Surface]):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.images = images

        self.create_bg_image()
    
    def create_bg_image(self) -> None:

        half_screen = pg.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h / 2)
        self.bg_image = pg.Surface((self.rect.w, self.rect.h))
        self.bg_image.fill(TERRAIN_COLORS["sky"], half_screen)
        half_screen.move_ip(0, self.rect.h / 2)
        self.bg_image.fill(TERRAIN_COLORS["ground"], half_screen)
    
    def render(self) -> None:
        
        self.image.blit(self.bg_image, self.rect)
        game_mode = environment.mode
        self.render_enemies(game_mode)
        self.render_players(game_mode)
    
    def get_horizontal_displacement_enemy(self, 
        i: int,
        mode: int) -> float:

        x_disp = 0

        #stepping forward to act
        if mode == MODE_ENEMY_ATTACK \
            and i == environment.current_character:
            
            x_disp = 64
        
        #swinging to attack
        if mode == MODE_ENEMY_ATTACK \
            and i == environment.current_character \
            and environment.t >= 0 and environment.t <= 15:
            x_disp += 16 * math.sin(environment.t * 2 * math.pi / 15)
        
        #knocked back by attack
        if mode == MODE_MEMBER_ATTACK \
            and i == environment.selected_character \
            and (environment.next_action == ACTION_ATTACK \
                or environment.next_action == ACTION_HARM_SPELL) \
            and environment.t >= 45 and environment.t <= 60:
            x_disp -= 16 * math.sin((environment.t - 45) * 2 * math.pi / 15)

        return x_disp

    def get_horizontal_displacement_player(self,
        i: int,
        mode: int) -> float:

        x_disp = 0

        #stepping forward to act
        if mode != MODE_ENEMY_ATTACK \
            and i == environment.current_character:
            x_disp = -64
        
        #swinging to attack
        if mode == MODE_MEMBER_ATTACK \
            and i == environment.current_character \
            and environment.t >= 0 and environment.t <= 15:
            x_disp -= 16 * math.sin(environment.t * 2 * math.pi / 15)
        
        #knocked back by attack
        if mode == MODE_ENEMY_ATTACK \
            and i == environment.selected_character \
            and environment.t >= 45 and environment.t <= 60:
            x_disp += 16 * math.sin((environment.t - 45) * 2 * math.pi / 15)

        return x_disp

    def render_character(self,
        character: model.Character,
        x_disp: float,
        cursor_x: float,
        cursor_y: float) -> None:

        #draw sprite
        self.image.blit(
            source = self.images[character.type],
            dest = (x_disp + cursor_x, cursor_y)
        )

        #draw health bar
        self.image.fill(
            BLACK,
            pg.Rect(cursor_x + x_disp, cursor_y - 16, 36, 4)
        )
        proportion = character.hp / character.hp_max
        self.image.fill(
            RED,
            pg.Rect(cursor_x + x_disp + 2, cursor_y - 14, 32 * proportion, 2)
        )

        #draw magic bar
        self.image.fill(
            BLACK,
            pg.Rect(cursor_x + x_disp, cursor_y - 8, 36, 4)
        )
        if character.mp_max != 0:
            proportion = character.mp / character.mp_max
        else:
            proportion = 0
        self.image.fill(
            BLUE,
            pg.Rect(cursor_x + x_disp + 2, cursor_y - 6, 32 * proportion, 2)
        )
        
    def render_enemies(self, mode: int) -> None:

        cursor_x = 128
        cursor_y = self.rect.h / 2
        enemy = environment.enemy_leader
        i = 0
        while enemy is not None:
            cursor_x -= 24
            cursor_y += 32

            #alive?
            if (enemy.type >= 0 and enemy.hp != 0):

                x_disp = self.get_horizontal_displacement_enemy(i, mode)

                #highlight if selected
                if mode == MODE_ENEMY_SELECT \
                    and i == environment.selected_character:

                    self.image.fill(WHITE, pg.Rect(cursor_x + x_disp - 2, cursor_y - 2, 36, 36))

                self.render_character(enemy, x_disp, cursor_x, cursor_y)
                
            
            enemy = enemy.next
            i += 1
    
    def render_players(self, mode: int) -> None:

        cursor_x = self.rect.w - 128
        cursor_y = self.rect.h / 2
        member = environment.party_leader
        i = 0
        while member is not None:
            cursor_x += 24
            cursor_y += 32

            #alive?
            if (member.type >= 0 and member.hp != 0):

                x_disp = self.get_horizontal_displacement_player(i, mode)
                
                #highlight if selected
                if mode == MODE_MEMBER_SELECT \
                    and i == environment.selected_character:

                    self.image.fill(WHITE, pg.Rect(cursor_x + x_disp - 2, cursor_y - 2, 36, 36))

                self.render_character(member, x_disp, cursor_x, cursor_y)
            
            member = member.next
            i += 1

class Panel(pg.sprite.Sprite):

    def __init__(self,
        rect: pg.Rect,
        font: pg.font.Font):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(BUTTON_INACTIVE_COLOR)
        self.font = font
    
    def render(self,
        items: list[str],
        selected: int) -> None:

        self.image.fill(BUTTON_INACTIVE_COLOR)

        cursor = pg.Rect(4, 4, self.rect.w, 16)
        for i,text in enumerate(items):

            if i == selected:
                self.image.fill(color = BUTTON_ACTIVE_COLOR, rect = cursor)
            temp_surface = self.font.render(text, SCREEN_TEXT_COLOR)[0]
            self.image.blit(source = temp_surface, dest = cursor)
            cursor.move_ip(0, 16)

class Renderer:


    def __init__(self):

        self.screen_surface = pg.display.set_mode(SCREEN_SIZE)
        self.create_assets()
        self.create_layouts()
    
    def create_assets(self) -> None:

        self.images = {
            model.SOLDIER: pg.Surface((32,32)),
            model.MAGE: pg.Surface((32,32)),
            model.RAT: pg.Surface((32,32)),
            model.CULTIST: pg.Surface((32,32)),
        }

        for character_type in CHARACTER_COLORS:
            self.images[character_type].fill(CHARACTER_COLORS[character_type])

        fontLib.init()
        self.screen_font = fontLib.SysFont("arial", SCREEN_TEXT_SIZE)
    
    def create_layouts(self) -> None:

        self.map_view = MapView(
            pg.Rect(0,0,SCREEN_SIZE[0], SCREEN_SIZE[1]),
            self.images
        )

        self.menu_panel = Panel(
            pg.Rect(32, SCREEN_SIZE[1] - 64, 512, 64),
            self.screen_font
        )
    
    def draw(self) -> None:

        self.map_view.render()
        self.screen_surface.blit(self.map_view.image, self.map_view.rect)

        game_mode = environment.mode

        item_list = []
        if game_mode == MODE_ACTION_SELECT:
            item_list = environment.actions
        elif game_mode == MODE_SPELL_SELECT:
            item_list = environment.spells
        elif game_mode == MODE_ITEM_SELECT:
            item_list = environment.items
        self.menu_panel.render(
            item_list,
            environment.current_action
        )

        self.screen_surface.blit(self.menu_panel.image, self.menu_panel.rect)

        pg.display.flip()

renderer_context = Renderer()