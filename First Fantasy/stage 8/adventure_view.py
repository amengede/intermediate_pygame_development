from config import *
import model

BLACK = (0,0,0)
WHITE = (255, 255, 255)
BG_HIGHLIGHT_COLOR = (64, 160, 224)
TEXT_PANEL_COLOR = BLACK
PLAYER_COLOR = (128, 32, 128)
BUTTON_INACTIVE_COLOR = (128, 128, 128)
BUTTON_ACTIVE_COLOR = (128, 192, 255)
BUTTON_TEXT_COLOR = (32, 32, 32)
NPC_COLOR = BG_HIGHLIGHT_COLOR

TERRAIN_COLORS = {
    TERRAIN_GROUND: (69, 39, 2),
    TERRAIN_RADIATED_GROUND: (40, 240, 5),
    TERRAIN_BLOCKED: (192, 0, 0)
}

SCREEN_TEXT_SIZE = 24
SCREEN_TEXT_COLOR = WHITE

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
        images: dict[int,pg.Surface]):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(bgColor)
        self.color = bgColor
        self.images = images
    
    def render(self,
        terrain: dict[int, pg.sprite.Group],
        player: model.Player,
        villagers: pg.sprite.Group) -> None:

        self.image.fill(self.color)

        for block_type in terrain:
            for block in terrain[block_type].sprites():
                self.image.blit(
                    source = self.images[block_type],
                    dest = block.rect
                )
        
        for villager in villagers.sprites():
            display_direction = SPRITE_DIRECTIONS[villager.direction_descriptor]
            current_image = self.images[NPC][display_direction][int(villager.step)]
            self.image.blit(
                current_image,
                villager.rect
            )
        
        display_direction = SPRITE_DIRECTIONS[player.direction_descriptor]
        current_image = self.images[PLAYER][display_direction][int(player.step)]
        self.image.blit(current_image, player.rect)

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
        images: dict[int,pg.Surface]):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(bgColor)
        self.color = bgColor
        self.images = {}
        self.scale_images(images)
    
    def scale_images(self, images):

        scale_factor = self.rect.w / SCREEN_SIZE[0]
        for image_type in images:

            if image_type not in (PLAYER, NPC):
                original_image = images[image_type]
                new_width = int(original_image.get_width() * scale_factor)
                new_height = int(original_image.get_height() * scale_factor)
                self.images[image_type] = pg.transform.scale(original_image, (new_width, new_height))
            else:
                self.images[image_type] = {}
                for direction in images[image_type]:
                    self.images[image_type][direction] = []
                    for i in range(3):
                        original_image = images[image_type][direction][i]
                        new_width = int(original_image.get_width() * scale_factor)
                        new_height = int(original_image.get_height() * scale_factor)
                        self.images[image_type][direction].append(
                            pg.transform.scale(original_image, (new_width, new_height))
                        )

    def render(self,
        terrain: dict[int, pg.sprite.Group],
        player: model.Player,
        villagers: pg.sprite.Group) -> None:

        self.image.fill(self.color)

        player_rect = player.rect
        dx = -player_rect.centerx
        dy = -player_rect.centery
        scale_factor = self.rect.w / SCREEN_SIZE[0]
        cen_x = self.rect.w / 2
        cen_y = self.rect.h / 2
        for block_type in terrain:
            for block in terrain[block_type].sprites():

                translated_rect = block.rect.move(dx, dy)
                translated_rect.x *= scale_factor
                translated_rect.y *= scale_factor
                translated_rect.move_ip(cen_x, cen_y)
                self.image.blit(
                    source = self.images[block_type],
                    dest = translated_rect
                )
        
        for villager in villagers.sprites():
            translated_rect = villager.rect.move(dx, dy)
            translated_rect.x *= scale_factor
            translated_rect.y *= scale_factor
            translated_rect.move_ip(cen_x, cen_y)
            display_direction = SPRITE_DIRECTIONS[villager.direction_descriptor]
            current_image = self.images[NPC][display_direction][int(villager.step)]
            self.image.blit(
                current_image,
                translated_rect
            )
        
        translated_rect = player_rect.move(dx, dy)
        translated_rect.x *= scale_factor
        translated_rect.y *= scale_factor
        translated_rect.move_ip(cen_x, cen_y)
        display_direction = SPRITE_DIRECTIONS[player.direction_descriptor]
        current_image = self.images[PLAYER][display_direction][int(player.step)]
        self.image.blit(current_image, translated_rect)

class Button(pg.sprite.Sprite):

    def __init__(self,
        rect: pg.Rect,
        font: pg.font.Font,
        label: str):

        super().__init__()
        self.rect = rect
        self.image = pg.Surface((rect.w, rect.h))
        self.image.fill(BUTTON_INACTIVE_COLOR)
        self.font = font
        self.callback = None
        self.label = label
    
    def set_callback(self, callback: Callable[[],None]) -> None:
        self.callback = callback
    
    def update(self, **kwargs) -> None:
        
        mouse_x, mouse_y = kwargs["mouse_pos"]
        if self.rect.collidepoint(mouse_x, mouse_y):
            self.image.fill(BUTTON_ACTIVE_COLOR)
            if kwargs["click_event"] and self.callback is not None:
                self.callback()
        else:
            self.image.fill(BUTTON_INACTIVE_COLOR)
        
    def render(self) -> None:

        temp_surface = self.font.render(
            text = self.label,
            fgcolor = BUTTON_TEXT_COLOR
        )[0]
        self.image.blit(
            source = temp_surface,
            dest = (8,8)
        )

class DialogueView(pg.sprite.Sprite):

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
    
    def render(self, line: str) -> None:

        self.image.fill(self.color)
        temp_surface = self.font.render(
            text = line, 
            fgcolor = SCREEN_TEXT_COLOR
        )[0]
        self.image.blit(
            source = temp_surface, 
            dest = (32,8)
        )

class Renderer:


    def __init__(self):

        self.screen_surface = pg.display.set_mode(SCREEN_SIZE)
        self.create_assets()
        self.create_layouts()
    
    def create_assets(self) -> None:

        self.images = {
            PLAYER: {
                NORTH: [],
                EAST: [],
                SOUTH: [],
                WEST: []
            },
            NPC: {
                NORTH: [],
                EAST: [],
                SOUTH: [],
                WEST: []
            }
        }

        temp_surface = pg.image.load("gfx/grass.jpg").convert()
        self.images[TERRAIN_GROUND] = pg.transform.scale(
            temp_surface, (32,32)
        )
        temp_surface = pg.image.load("gfx/radiated.jpg").convert()
        self.images[TERRAIN_RADIATED_GROUND] = pg.transform.scale(
            temp_surface, (32,32)
        )
        temp_surface = pg.image.load("gfx/lava.jpg").convert()
        self.images[TERRAIN_BLOCKED] = pg.transform.scale(
            temp_surface, (32,32)
        )
        
        for i in range(3):

            temp_surface = pg.image.load(f"gfx/mage_north_{i}.png").convert_alpha()
            self.images[PLAYER][NORTH].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/mage_east_{i}.png").convert_alpha()
            self.images[PLAYER][EAST].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/mage_south_{i}.png").convert_alpha()
            self.images[PLAYER][SOUTH].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/mage_west_{i}.png").convert_alpha()
            self.images[PLAYER][WEST].append(
                pg.transform.scale(temp_surface, (24,24))
            )

            temp_surface = pg.image.load(f"gfx/villager_north_{i}.png").convert_alpha()
            self.images[NPC][NORTH].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/villager_east_{i}.png").convert_alpha()
            self.images[NPC][EAST].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/villager_south_{i}.png").convert_alpha()
            self.images[NPC][SOUTH].append(
                pg.transform.scale(temp_surface, (24,24))
            )
            temp_surface = pg.image.load(f"gfx/villager_west_{i}.png").convert_alpha()
            self.images[NPC][WEST].append(
                pg.transform.scale(temp_surface, (24,24))
            )

        fontLib.init()
        self.screen_font = fontLib.SysFont("arial", SCREEN_TEXT_SIZE)
    
    def create_layouts(self) -> None:

        self.map_view = MapView(
            pg.Rect(0,0,SCREEN_SIZE[0], SCREEN_SIZE[1]),
            BLACK, self.images
        )
        self.mini_map_view = MiniMapView(
            pg.Rect(SCREEN_SIZE[0] - 128, 0, 128, 128),
            BLACK, self.images
        )
        self.dialogue_view = DialogueView(
            pg.Rect(64, SCREEN_SIZE[1] - 64, 512, 64),
            BLACK, self.screen_font
        )
    
    def draw(self,
        terrain: dict[int,pg.sprite.Group],
        player: model.Player,
        villagers: pg.sprite.Group,
        line: str) -> None:

        self.map_view.render(terrain,player,villagers)
        self.mini_map_view.render(terrain,player,villagers)
        self.screen_surface.blit(self.map_view.image,self.map_view.rect)
        self.screen_surface.blit(self.mini_map_view.image, self.mini_map_view.rect)

        if line:
            self.dialogue_view.render(line)
            self.screen_surface.blit(self.dialogue_view.image, self.dialogue_view.rect)

        pg.display.flip()

    def save_screen(self) -> None:
        self.saved_screen = self.screen_surface.copy()
    
    def render_saved_screen(self, proportion: float) -> None:

        self.saved_screen.fill(BLACK, pg.Rect(0,0,SCREEN_SIZE[0] * proportion, SCREEN_SIZE[1]))
        self.screen_surface.blit(self.saved_screen, (0,0))
        pg.display.flip()

renderer_context = Renderer()