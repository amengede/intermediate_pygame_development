from config import *
import model

BG_COLOR = (32, 128, 192)
BG_HIGHLIGHT_COLOR = (64, 160, 224)
TEXT_PANEL_COLOR = (0,0,0)
PLAYER_COLOR = (128, 32, 128)
BUTTON_INACTIVE_COLOR = (128, 128, 128)
BUTTON_ACTIVE_COLOR = (128, 192, 255)
BUTTON_TEXT_COLOR = (32, 32, 32)

BLOCK_COLOR = {
    BLOCK_STATUS_INACTIVE: (192, 192, 192),
    BLOCK_STATUS_ACTIVE: (255, 192, 192)
}

SPRITE_PLAYER = 0
SPRITE_INACTIVE_BLOCK = 1
SPRITE_ACTIVE_BLOCK = 2

SCREEN_TEXT_SIZE = 24
SCREEN_TEXT_COLOR = (192, 128, 64)

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
        bgColor: tuple[int], 
        images: dict[int,pg.Surface]):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(bgColor)
        self.color = bgColor
        self.images = images
    
    def render(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.image.fill(self.color)

        for block in inactive:
            self.image.blit(
                source = self.images[SPRITE_INACTIVE_BLOCK], 
                dest = block.get_rect()
            )
        
        for block in active:
            self.image.blit(
                source = self.images[SPRITE_ACTIVE_BLOCK], 
                dest = block.get_rect()
            )
        
        player_rect = player.get_rect()
        self.image.blit(
            source = self.images[SPRITE_PLAYER], 
            dest = player_rect
        )

class StatusView(pg.sprite.Sprite):

    def __init__(
        self, 
        rect: pg.Rect, 
        bgColor: tuple[int], 
        font: pg.font.Font):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(bgColor)
        self.color = bgColor
        self.font = font
        self.screen_scroll_x = 128
    
    def render(self, player_rect: pg.Rect) -> None:

        self.screen_scroll_x -= 1
        if self.screen_scroll_x < -128:
            self.screen_scroll_x = 128

        self.image.fill(self.color)
        temp_surface = self.font.render(
            text = f"Player x = {player_rect.centerx}", 
            fgcolor = SCREEN_TEXT_COLOR
        )[0]
        self.image.blit(
            source = temp_surface, 
            dest = (self.screen_scroll_x,8)
        )

        temp_surface = self.font.render(
            text = f"Player y = {player_rect.centery}", 
            fgcolor = SCREEN_TEXT_COLOR
        )[0]
        self.image.blit(
            source = temp_surface, 
            dest = (self.screen_scroll_x,40)
        )

class MiniMapView(pg.sprite.Sprite):

    def __init__(
        self, 
        rect: pg.Rect, 
        bgColor: tuple[int], 
        images: dict[int,pg.Surface]):

        super().__init__()
        self.rect = pg.rect.Rect(rect.x, rect.y, 2 * rect.w, 2 * rect.h)
        self.original_image = pg.Surface((rect.w, rect.h))
        self.original_image.fill(bgColor)
        self.color = bgColor
        self.images = images
    
    def render(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.original_image.fill(BG_HIGHLIGHT_COLOR)
        player_rect = player.get_rect()
        transformed_rect = pg.Rect((0,0,0,0))

        for block in inactive:
            transformed_rect = block.get_rect().move(
                32 - player_rect.centerx, 32 - player_rect.centery
            )
            self.original_image.blit(
                source = self.images[SPRITE_INACTIVE_BLOCK], 
                dest = transformed_rect
            )
        
        for block in active:
            transformed_rect = block.get_rect().move(
                32 - player_rect.centerx, 32 - player_rect.centery
            )
            self.original_image.blit(
                source = self.images[SPRITE_ACTIVE_BLOCK], 
                dest = transformed_rect
            )
        
        transformed_rect = player_rect.move(
            32 - player_rect.centerx, 32 - player_rect.centery
        )
        self.original_image.blit(
            source = self.images[SPRITE_PLAYER], 
            dest = transformed_rect
        )

        self.image = pg.transform.scale2x(self.original_image)

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
            SPRITE_PLAYER: pg.Surface((32,32)),
            SPRITE_INACTIVE_BLOCK: pg.Surface((32,32)),
            SPRITE_ACTIVE_BLOCK: pg.Surface((32,32))
        }

        self.images[SPRITE_PLAYER].fill(PLAYER_COLOR)
        self.images[SPRITE_INACTIVE_BLOCK].fill(BLOCK_COLOR[BLOCK_STATUS_INACTIVE])
        self.images[SPRITE_ACTIVE_BLOCK].fill(BLOCK_COLOR[BLOCK_STATUS_ACTIVE])

        fontLib.init()
        self.screen_font = fontLib.SysFont("arial", SCREEN_TEXT_SIZE)
    
    def create_layouts(self) -> None:

        self.buttons = pg.sprite.Group()
        self.layout = VStack(0,0,SCREEN_SIZE[0], SCREEN_SIZE[1], (0,0,0))
        self.top_bar = HStack(0, 0, SCREEN_SIZE[0], 192, (0,0,0))
        self.layout.add(self.top_bar, 0,0)
        self.status_text = StatusView(
            pg.Rect(0,0,128,64), 
            (0,0,0), 
            self.screen_font
        )
        self.top_bar.add(self.status_text, 32, 32)
        self.jump_button = Button(pg.Rect(0,0, 96, 32), self.screen_font, "Jump")
        self.buttons.add(self.jump_button)
        self.top_bar.add(self.jump_button, 32, 32)
        self.status_mini_map = MiniMapView(
            pg.Rect(0,0,64,64),
            BG_HIGHLIGHT_COLOR,
            self.images
        )
        self.top_bar.add(self.status_mini_map, 192, 32)
        self.map_view = MapView(
            pg.Rect(0,0,SCREEN_SIZE[0], SCREEN_SIZE[1] - 192),
            BG_COLOR,
            self.images
        )
        self.layout.add(self.map_view, 0,0)
    
    def set_jump_callback(self, callback: Callable[[],None]) -> None:
        self.jump_button.set_callback(callback)
    
    def update(self, mouse_pos: tuple[int], click_event: bool) -> None:
        self.buttons.update(mouse_pos = mouse_pos, click_event = click_event)
    
    def draw(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.map_view.render(player, active, inactive)
        self.status_text.render(player.get_rect())
        self.jump_button.render()
        self.status_mini_map.render(player, active, inactive)
        self.top_bar.draw()
        self.layout.draw()
        self.screen_surface.blit(self.layout.image,(0,0))

        pg.display.flip()

renderer_context = Renderer()