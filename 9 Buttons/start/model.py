from config import *

class Player(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x - 16,
            y - 16,
            32, 32
        )
    
    def move(self, amount: tuple[float]) -> None:

        dx,dy = amount
        self.rect.x = min(
            SCREEN_SIZE[0] - self.rect.w, 
            max(
                0, self.rect.x + dx
            )
        )
        self.rect.y = min(
            SCREEN_SIZE[1] - self.rect.h, 
            max(
                0, self.rect.y + dy
            )
        )
    
    def get_rect(self) -> pg.Rect:
        return self.rect

class Block(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x - 16,
            y - 16,
            32, 32
        )

    def get_rect(self) -> pg.Rect:
        return self.rect
    
class GameLogic:

    def __init__(self):

        self.blocks = pg.sprite.Group()
        self.visible_sprites = pg.sprite.Group()
        self.inactive_blocks = pg.sprite.Group()
        self.active_blocks = pg.sprite.Group()

        self.player = Player(320, 240)
        self.visible_sprites.add(self.player)

        self.reset_state()
        self.load_random_state()
    
    def reset_state(self):
        
        for block in self.blocks.sprites():
            block.kill()

    def load_random_state(self):
        for _ in range(16):
            new_block = Block(
                random.randint(0, 640),
                random.randint(300, 480)
            )
            self.blocks.add(new_block)
            self.visible_sprites.add(new_block)
    
    def can_move(self) -> bool:

        self.inactive_blocks.empty()
        self.active_blocks.empty()

        can_move = True
        hit_blocks = pg.sprite.spritecollide(
            sprite = self.player, 
            group = self.blocks, 
            dokill = False
        )
        can_move = len(hit_blocks) == 0
        for block in self.blocks.sprites():
            if block in hit_blocks:
                self.active_blocks.add(block)
            else:
                self.inactive_blocks.add(block)
        return can_move

    def get_player(self) -> Player:
        return self.player
    
    def get_inactive_blocks(self) -> list[Block]:
        return self.inactive_blocks.sprites()
    
    def get_active_blocks(self) -> list[Block]:
        return self.active_blocks.sprites()
    
    def move_player(self, movement: list[float]) -> None:

        self.player.move(movement)
        if not self.can_move():
            movement[0] *= -1
            movement[1] *= -1
            self.player.move(movement)

game_context = GameLogic()