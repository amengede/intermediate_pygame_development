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

class GameLogic:

    def __init__(self):

        self.blocks = pg.sprite.Group()
        self.visible_sprites = pg.sprite.Group()

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

        can_move = True
        hit_blocks = pg.sprite.spritecollide(
            sprite = self.player, 
            group = self.blocks, 
            dokill = False
        )
        can_move = len(hit_blocks) == 0
        for block in self.blocks.sprites():
            block.set_active(block in hit_blocks)
        return can_move

    def handle_keys(self) -> None:

        movement_speed = 1
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
        self.player.move(movement)
        
        if not self.can_move():
            movement[0] *= -1
            movement[1] *= -1
            self.player.move(movement)
    
    def update(self):
        self.handle_keys()
        self.visible_sprites.update()
    
    def draw(self, surface: pg.Surface):
        self.visible_sprites.draw(surface)

game_context = GameLogic()