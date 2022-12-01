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

class Renderer:


    def __init__(self):

        self.screen_surface = pg.display.set_mode(SCREEN_SIZE)
        self.banner_surface = pg.Surface((128, 64))
        self.zoomed_in_surface = pg.Surface((64,64))

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
        self.screen_scroll_x = 128
    
    def draw(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.screen_surface.fill(BG_COLOR)

        for block in inactive:
            self.screen_surface.blit(
                source = self.images[SPRITE_INACTIVE_BLOCK], 
                dest = block.get_rect()
            )
        
        for block in active:
            self.screen_surface.blit(
                source = self.images[SPRITE_ACTIVE_BLOCK], 
                dest = block.get_rect()
            )
        
        player_rect = player.get_rect()
        self.screen_surface.blit(
            source = self.images[SPRITE_PLAYER], 
            dest = player_rect
        )

        self.render_text_panel(player_rect)
        self.screen_surface.blit(self.banner_surface, (32,32))

        self.render_zoomed_in_view(player, active, inactive)
        transformed_surface = pg.transform.scale2x(self.zoomed_in_surface)
        self.screen_surface.blit(transformed_surface, (640-160, 32))

        pg.display.flip()
    
    def render_text_panel(self, player_rect: pg.Rect) -> None:

        self.screen_scroll_x -= 1
        if self.screen_scroll_x < -128:
            self.screen_scroll_x = 128

        self.banner_surface.fill(TEXT_PANEL_COLOR)
        temp_surface = self.screen_font.render(
            text = f"Player x = {player_rect.centerx}", 
            fgcolor = SCREEN_TEXT_COLOR
        )[0]
        self.banner_surface.blit(
            source = temp_surface, 
            dest = (self.screen_scroll_x,8)
        )

        temp_surface = self.screen_font.render(
            text = f"Player y = {player_rect.centery}", 
            fgcolor = SCREEN_TEXT_COLOR
        )[0]
        self.banner_surface.blit(
            source = temp_surface, 
            dest = (self.screen_scroll_x,40)
        )

    def render_zoomed_in_view(self,
        player: model.Player, 
        active: list[model.Block], 
        inactive: list[model.Block]) -> None:

        self.zoomed_in_surface.fill(BG_HIGHLIGHT_COLOR)
        player_rect = player.get_rect()
        transformed_rect = pg.Rect((0,0,1,1))

        for block in inactive:
            transformed_rect = block.get_rect().move(
                32 - player_rect.centerx, 32 - player_rect.centery
            )
            self.zoomed_in_surface.blit(
                source = self.images[SPRITE_INACTIVE_BLOCK], 
                dest = transformed_rect
            )
        
        for block in active:
            transformed_rect = block.get_rect().move(
                32 - player_rect.centerx, 32 - player_rect.centery
            )
            self.zoomed_in_surface.blit(
                source = self.images[SPRITE_ACTIVE_BLOCK], 
                dest = transformed_rect
            )
        
        transformed_rect = player_rect.move(
            32 - player_rect.centerx, 32 - player_rect.centery
        )
        self.zoomed_in_surface.blit(
            source = self.images[SPRITE_PLAYER], 
            dest = transformed_rect
        )

renderer_context = Renderer()