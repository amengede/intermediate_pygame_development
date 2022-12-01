from config import *

class Player(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pg.Surface((32,32))
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
    
    def update(self) -> None:
        self.image.fill(PLAYER_COLOR)

class Block(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pg.Surface((32,32))
        self.rect = pg.Rect(
            x - 16,
            y - 16,
            32, 32
        )
        self.active = False
      
    def set_active(self, status: bool) -> None:
        self.active = status
    
    def update(self) -> None:
        color = BLOCK_COLOR[BLOCK_STATUS_INACTIVE]
        if self.active:
            color = BLOCK_COLOR[BLOCK_STATUS_ACTIVE]
        self.image.fill(color)