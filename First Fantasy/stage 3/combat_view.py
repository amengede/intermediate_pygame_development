from config import *
import combat_model

BLACK = (0,0,0)
WHITE = (255, 255, 255)
BG_HIGHLIGHT_COLOR = (64, 160, 224)
TEXT_PANEL_COLOR = BG_HIGHLIGHT_COLOR
PLAYER_COLOR = (128, 32, 128)
BUTTON_INACTIVE_COLOR = (128, 128, 128)
BUTTON_ACTIVE_COLOR = (128, 192, 255)
BUTTON_TEXT_COLOR = (32, 32, 32)

CHARACTER_COLORS = {
    combat_model.SOLDIER: (0, 0, 128),
    combat_model.MAGE: (0, 128, 0),
    combat_model.RAT: (128, 0, 0),
    combat_model.CULTIST: (128, 0, 128)
}

TERRAIN_COLORS = {
    "sky": BG_HIGHLIGHT_COLOR,
    "ground": (69, 39, 2)
}

SCREEN_TEXT_SIZE = 24
SCREEN_TEXT_COLOR = WHITE

class VStack(pg.sprite.Sprite):

    def __init__(self, x, y, w, h, bgColor):

        super().__init__()
        self.rect = pg.Rect(x,y,w,h)
        self.image = pg.Surface((w,h))
        self.image.fill(bgColor)
        self.y_bottom = y
        self.contents = pg.sprite.Group()
    
    def add(self, widget: pg.sprite.Sprite,
        x_offset: float, y_offset: float) -> None:

        self.contents.add(widget)
        self.y_bottom += y_offset
        widget.rect.move_ip(x_offset, self.y_bottom)
        self.y_bottom += widget.rect.h
    
    def draw(self) -> None:
        self.contents.draw(self.image)

class HStack(pg.sprite.Sprite):

    def __init__(self, x, y, w, h, bgColor):

        super().__init__()
        self.rect = pg.Rect(x,y,w,h)
        self.image = pg.Surface((w,h))
        self.image.fill(bgColor)
        self.x_right = x
        self.contents = pg.sprite.Group()
    
    def add(self, widget: pg.sprite.Sprite,
        x_offset: float, y_offset: float) -> None:

        self.contents.add(widget)
        self.x_right += x_offset
        widget.rect.move_ip(self.x_right, y_offset)
        self.x_right += widget.rect.w
    
    def draw(self) -> None:
        self.contents.draw(self.image)

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
    
    def render(self,
        enemy_leader: combat_model.Character,
        party_leader: combat_model.Character) -> None:
        
        self.image.blit(self.bg_image, self.rect)

        cursor_x = self.rect.x + 128
        cursor_y = self.rect.y + self.rect.h / 2
        enemy = enemy_leader
        while enemy is not None:
            cursor_x -= 24
            cursor_y += 32

            if (enemy.get_type() >= 0 and enemy.get_hp() != 0):
                self.image.blit(
                    source = self.images[enemy.get_type()],
                    dest = (cursor_x, cursor_y)
                )
            
            enemy = enemy.get_next()
        
        cursor_x = self.rect.x + self.rect.w - 128
        cursor_y = self.rect.y + self.rect.h / 2
        member = party_leader
        while member is not None:
            cursor_x += 24
            cursor_y += 32

            if (member.get_type() >= 0 and member.get_hp() != 0):
                self.image.blit(
                    source = self.images[member.get_type()],
                    dest = (cursor_x, cursor_y)
                )
            
            member = member.get_next()

class Button(pg.sprite.Sprite):

    def __init__(self,
        rect: pg.Rect,
        font: pg.font.Font,
        label: str):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(BUTTON_INACTIVE_COLOR)
        self.font = font
        self.callback = None
        self.label = label
    
    def set_callback(self, callback: Callable[[],None]) -> None:
        self.callback = callback
    
    def update(self, **kwargs) -> None:
        
        mouse_x, mouse_y = kwargs["mouse_pos"]
        if self.rect.collidepoint(mouse_x, mouse_y):
            self.image.fill(BUTTON_ACTIVE_COLOR)
            if kwargs["click_event"] and self.callback is not None:
                self.callback()
        else:
            self.image.fill(BUTTON_INACTIVE_COLOR)
        
    def render(self) -> None:

        temp_surface = self.font.render(
            text = self.label,
            fgcolor = BUTTON_TEXT_COLOR
        )[0]
        self.image.blit(
            source = temp_surface,
            dest = (8,8)
        )

class Renderer:


    def __init__(self):

        self.screen_surface = pg.display.set_mode(SCREEN_SIZE)
        self.create_assets()
        self.create_layouts()
    
    def create_assets(self) -> None:

        self.images = {
            combat_model.SOLDIER: pg.Surface((32,32)),
            combat_model.MAGE: pg.Surface((32,32)),
            combat_model.RAT: pg.Surface((32,32)),
            combat_model.CULTIST: pg.Surface((32,32)),
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
    
    def draw(self,
        enemy_leader: combat_model.Character,
        party_leader: combat_model.Character) -> None:

        self.map_view.render(enemy_leader, party_leader)
        self.screen_surface.blit(self.map_view.image, self.map_view.rect)

        pg.display.flip()

renderer_context = Renderer()