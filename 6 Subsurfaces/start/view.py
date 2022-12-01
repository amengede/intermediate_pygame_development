from config import *
import model

BG_COLOR = (32, 128, 192)
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
        self.screen_font.render_to(
            surf = self.screen_surface, 
            dest = (32,32), 
            text = f"Player x = {player_rect.centerx}", 
            fgcolor = SCREEN_TEXT_COLOR
        )
        self.screen_font.render_to(
            surf = self.screen_surface, 
            dest = (32,64), 
            text = f"Player y = {player_rect.centery}", 
            fgcolor = SCREEN_TEXT_COLOR
        )

        pg.display.flip()

renderer_context = Renderer()