from config import *
import io

TERRAIN_GROUND = 0
TERRAIN_RADIATED_GROUND = 1
TERRAIN_BLOCKED = 2
PLAYER = 3

class Player(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x - 12,
            y - 12,
            24, 24
        )
    
    def move(self, amount: tuple[float]) -> None:

        dx,dy = amount
        self.rect.x = self.rect.x + dx
        self.rect.y = self.rect.y + dy
    
    def get_rect(self) -> pg.Rect:
        return self.rect

class Block(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x,
            y,
            32, 32
        )

    def get_rect(self) -> pg.Rect:
        return self.rect
    
class GameLogic:

    def __init__(self):

        self.terrain = {
            TERRAIN_GROUND: pg.sprite.Group(),
            TERRAIN_RADIATED_GROUND: pg.sprite.Group(),
            TERRAIN_BLOCKED: pg.sprite.Group()
        }
        self.transient_state = pg.sprite.Group()

        self.player = Player(320, 240)

        self.reset_state()
    
    def reset_state(self) -> None:
        
        for sprite in self.transient_state.sprites():
            sprite.kill()

    def load_from_file(self, filename: str) -> None:
        
        with open(filename, mode = "r") as file:

            line = file.readline()
            while (line):

                if line[0] != "[":
                    raise Exception("Invalid line found")
                
                line = line.rstrip()[1:-1]

                if line == "terrain":
                    line = self.load_terrain_data(file)
                elif line == "player":
                    line = self.load_player_data(file)
                else:
                    raise Exception("Unkown header!")
    
    def load_terrain_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        row = 0
        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            line = line.split(" ")

            for col,block_type in enumerate(line):
                block_type = int(block_type)

                new_block = Block(32*col, 32*row)
                if block_type not in self.terrain:
                    raise Exception(f"Unknown block type: {block_type}")
                self.terrain[block_type].add(new_block)
                self.transient_state.add(new_block)

            line = file.readline()
            row += 1
        
        return ""
    
    def load_player_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            property, _, value = str.partition(line, " ")

            if property == "x":
                self.player.rect.centerx = float(value)
            elif property == "y":
                self.player.rect.centery = float(value)
            else:
                raise Exception(f"Unknown property: {property}")

            line = file.readline()
        
        return ""

    def player_can_move(self) -> bool:

        hit_blocks = pg.sprite.spritecollide(
            sprite = self.player, 
            group = self.terrain[TERRAIN_BLOCKED], 
            dokill = False
        )
        return len(hit_blocks) == 0

    def get_player(self) -> Player:
        return self.player
    
    def get_terrain(self) -> dict[int, pg.sprite.Group]:
        return self.terrain
    
    def move_player(self, movement: list[float]) -> None:

        self.player.move(movement)
        if not self.player_can_move():
            movement[0] *= -1
            movement[1] *= -1
            self.player.move(movement)

game_context = GameLogic()