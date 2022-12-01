import pygame as pg
import random

SCREEN_SIZE = (640, 480)
BG_COLOR = (32, 128, 192)
PLAYER_COLOR = (128, 32, 128)

BLOCK_STATUS_INACTIVE = 0
BLOCK_STATUS_ACTIVE = 1
BLOCK_COLOR = {
    BLOCK_STATUS_INACTIVE: (192, 192, 192),
    BLOCK_STATUS_ACTIVE: (255, 192, 192)
}

class Player:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.w = 32
        self.h = 32
        self.image = pg.Surface((32,32))
    
    def get_rect(self) -> pg.Rect:
        return pg.Rect(
            int(self.x - self.w // 2), 
            int(self.y - self.h // 2), 
            int(self.w),
            int(self.h)
        )
    
    def move(self, amount: tuple[float]) -> None:

        dx,dy = amount
        self.x = min(SCREEN_SIZE[0] - self.w // 2, max(self.w // 2, self.x + dx))
        self.y = min(SCREEN_SIZE[1] - self.h // 2, max(self.h // 2, self.y + dy))
    
    def draw(self, surface: pg.Surface) -> None:
        self.image.fill(PLAYER_COLOR)
        surface.blit(self.image, self.get_rect())

class Block:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.w = 32
        self.h = 32
        self.image = pg.Surface((32,32))
        self.active = False
    
    def get_rect(self) -> pg.Rect:
        return pg.Rect(
            int(self.x - self.w // 2), 
            int(self.y - self.h // 2), 
            int(self.w),
            int(self.h)
        )
    
    def overlaps_with(self, other_rect: pg.Rect) -> bool:
        
        our_rect = self.get_rect()
        return our_rect.colliderect(other_rect)
    
    def set_status(self, status):
        self.active = status
    
    def draw(self, surface: pg.Surface) -> None:
        color = BLOCK_COLOR[BLOCK_STATUS_INACTIVE]
        if self.active:
            color = BLOCK_COLOR[BLOCK_STATUS_ACTIVE]
        self.image.fill(color)
        surface.blit(self.image, self.get_rect())

def can_move(player: Player, blocks: list[Block]) -> bool:

    can_move = True
    player_rect = player.get_rect()
    for block in blocks:
        if block.overlaps_with(player_rect):
            can_move = False
            block.set_status(True)
        else:
            block.set_status(False)
    return can_move

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()
    player = Player(320, 240)
    movement_speed = 1

    blocks = []
    for _ in range(16):
        blocks.append(
            Block(
                random.randint(0, 640),
                random.randint(300, 480)
            )
        )

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        keys_pressed = pg.key.get_pressed()
        movement = [0,0]
        if keys_pressed[pg.K_LEFT]:
            movement[0] -= movement_speed
        if keys_pressed[pg.K_RIGHT]:
            movement[0] += movement_speed
        if keys_pressed[pg.K_UP]:
            movement[1] -= movement_speed
        if keys_pressed[pg.K_DOWN]:
            movement[1] += movement_speed
        player.move(movement)
        if not can_move(player, blocks):
            movement[0] *= -1
            movement[1] *= -1
            player.move(movement)
        
        
        screen_surface.fill(BG_COLOR)
        for block in blocks:
            block.draw(screen_surface)
        player.draw(screen_surface)
        
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()