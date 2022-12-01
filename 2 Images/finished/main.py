import pygame as pg
import math

SCREEN_SIZE = (640, 480)
BG_COLOR = (32, 128, 192)
SPRITE_SIZE = (128, 256)

def main() -> None:

    pg.init()
    screen_surface = pg.display.set_mode(SCREEN_SIZE)

    #load and convert the file, could use convert_alpha if the image
    #had an alpha channel we wanted to use.
    image = pg.image.load("gfx/skeleton.png").convert()

    t = 0.0
    screenhots_taken = 0
    running = True
    while running:

        t += 0.01
        t = t % 360

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                #take a screenshot
                pg.image.save(screen_surface, f"screenshot_{screenhots_taken}.png")
                screenhots_taken += 1
        
        #usually it's a good idea to store the original image,
        #then apply modifications and save those into a copy
        transformed_image = pg.transform.scale(image, SPRITE_SIZE)
        transformed_image = pg.transform.rotate(transformed_image, t)
        #the image will resize and drift if we don't re-center it.
        transformed_rect = transformed_image.get_rect(center = (200 + 64, 480 - 128))
        tint = (int(128 + 127 * math.sin(t)), 0, int(128 + 127 * math.cos(t)))
        transformed_image.fill(tint, special_flags = pg.BLEND_MULT)

        
        screen_surface.fill(BG_COLOR)
        screen_surface.blit(transformed_image, transformed_rect)
        
        pg.display.flip()

if __name__ == "__main__":
    main()