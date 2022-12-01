from config import *
import model

BG_COLOR = (32, 128, 192)
BG_HIGHLIGHT_COLOR = (64, 160, 224)
TEXT_PANEL_COLOR = (0,0,0)
PLAYER_COLOR = (128, 32, 128)

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
        images: dict[int, pg.Surface]):

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
        images: dict[int, pg.Surface]):

        super().__init__()
        self.rect = rect
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
        transformed_rect = pg.Rect((0,0,1,1))

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

class Renderer:


    def __init__(self):

        self.create_assets()
        self.create_layouts()
        
    def create_assets(self) -> None:

        self.screen_surface = pg.display.set_mode(SCREEN_SIZE)

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

        self.layout = VStack(0,0, SCREEN_SIZE[0], SCREEN_SIZE[1], TEXT_PANEL_COLOR)
        self.status_bar = HStack(0,0, SCREEN_SIZE[0], 192, TEXT_PANEL_COLOR)
        self.layout.add(self.status_bar, 0, 0)
        self.status_view = StatusView(pg.Rect(0,0,128, 64), TEXT_PANEL_COLOR, self.screen_font)
        self.status_bar.add(self.status_view, 32, 32)
        self.mini_map_view = MiniMapView(pg.Rect(0,0,64, 64), BG_COLOR, self.images)
        self.status_bar.add(self.mini_map_view, 256, 32)
        self.map_view = MapView(pg.Rect(0,0,SCREEN_SIZE[0], SCREEN_SIZE[1] - 192), BG_COLOR, self.images)
        self.layout.add(self.map_view, 0, 0)

    def draw(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.status_view.render(player.get_rect())
        self.mini_map_view.render(player, active, inactive)
        self.status_bar.draw()
        self.map_view.render(player, active, inactive)
        self.layout.draw()
        self.screen_surface.blit(self.layout.image, (0,0))

        pg.display.flip()

renderer_context = Renderer()