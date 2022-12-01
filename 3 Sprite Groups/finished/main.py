import pygame as pg
import random

SCREEN_SIZE = (640, 480)
BG_COLOR = (32, 128, 192)
PLAYER_COLOR = (128, 32, 128)

BLOCK_STATUS_INACTIVE = 0
BLOCK_STATUS_ACTIVE = 1
BLOCK_COLOR = {
    BLOCK_STATUS_INACTIVE : (192, 192, 192),
    BLOCK_STATUS_ACTIVE : (255, 192, 192)
}

class Player(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pg.Surface((32,32))
        self.rect = pg.Rect(
            x - 16, y - 16, 32, 32
        )
    
    def get_rect(self) -> pg.Rect:
        return self.rect
    
    def move(self, amount: list[float]) -> None:

        dx,dy = amount
        self.rect.x = min(SCREEN_SIZE[0] - self.rect.w, max(0, self.rect.x + dx))
        self.rect.y = min(SCREEN_SIZE[1] - self.rect.h, max(0, self.rect.y + dy))
    
    def update(self) -> None:
        self.image.fill(PLAYER_COLOR)

class Block(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pg.Surface((32,32))
        self.rect = pg.Rect(
            x - 16, y - 16, 32, 32
        )
        self.active = False
    
    def get_rect(self) -> pg.Rect:
        return self.rect
    
    def set_active(self, active: bool) -> None:
        self.active = active
    
    def update(self) -> None:
        color = BLOCK_COLOR[BLOCK_STATUS_INACTIVE]
        if self.active:
            color = BLOCK_COLOR[BLOCK_STATUS_ACTIVE]
        self.image.fill(color)

def can_move(player: Player, blocks: pg.sprite.Group) -> bool:

    hit_sprites = pg.sprite.spritecollide(sprite = player, group = blocks, dokill = False)
    can_move = len(hit_sprites) == 0
    for block in blocks.sprites():
        block.set_active(block in hit_sprites)
    return can_move

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()

    visible_sprites = pg.sprite.Group()
    blocks = pg.sprite.Group()
    player = Player(320, 240)
    visible_sprites.add(player)
    player_speed = 1

    for _ in range(16):

        new_block = Block(
                random.randint(0, 640),
                random.randint(300, 480)
            )
        visible_sprites.add(new_block)
        blocks.add(new_block)

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        keys_pressed = pg.key.get_pressed()
        movement = [0,0]
        if keys_pressed[pg.K_LEFT]:
            movement[0] -= player_speed
        if keys_pressed[pg.K_RIGHT]:
            movement[0] += player_speed
        if keys_pressed[pg.K_UP]:
            movement[1] -= player_speed
        if keys_pressed[pg.K_DOWN]:
            movement[1] += player_speed
        player.move(movement)
        if not can_move(player, blocks):
            movement[0] *= -1
            movement[1] *= -1
            player.move(movement)
        
        visible_sprites.update()
        
        screen_surface.fill(BG_COLOR)
        visible_sprites.draw(screen_surface)
        
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()