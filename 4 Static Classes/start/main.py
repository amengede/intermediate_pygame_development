from config import *
import classes

def can_move(player: classes.Player, blocks: pg.sprite.Group) -> bool:

    can_move = True
    hit_blocks = pg.sprite.spritecollide(
        sprite = player, 
        group = blocks, 
        dokill = False
    )
    can_move = len(hit_blocks) == 0
    for block in blocks.sprites():
        block.set_active(block in hit_blocks)
    return can_move

def handle_keys(player: classes.Player, blocks: pg.sprite.Group) -> None:

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
    player.move(movement)
    
    if not can_move(player, blocks):
        movement[0] *= -1
        movement[1] *= -1
        player.move(movement)

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()

    blocks = pg.sprite.Group()
    visible_sprites = pg.sprite.Group()

    player = classes.Player(320, 240)
    visible_sprites.add(player)

    for _ in range(16):
        new_block = classes.Block(
            random.randint(0, 640),
            random.randint(300, 480)
        )
        blocks.add(new_block)
        visible_sprites.add(new_block)

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        handle_keys(player, blocks)
        
        
        visible_sprites.update()
        
        screen_surface.fill(BG_COLOR)
        visible_sprites.draw(screen_surface)
        
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()