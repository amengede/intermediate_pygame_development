from config import *
import io
import model

TERRAIN_GROUND = 0
TERRAIN_RADIATED_GROUND = 1
TERRAIN_BLOCKED = 2
PLAYER = 3
NPC = 4

NORTH = 0
NORTH_EAST = 1
EAST = 2
SOUTH_EAST = 3
SOUTH = 4
SOUTH_WEST = 5
WEST = 6
NORTH_WEST = 7
NONE = 8
DIRECTIONS = {
    NORTH: [0,-1], 
    NORTH_EAST: [1, -1], 
    EAST: [1, 0],
    SOUTH_EAST: [1,1], 
    SOUTH: [0, 1], 
    SOUTH_WEST: [-1, 1],
    WEST: [-1, 0], 
    NORTH_WEST: [-1, -1],
    NONE: [0,0]
}
NPC_DIRECTIONS = (NORTH, EAST, SOUTH, WEST, NONE)

MODE_WALKING = 0
MODE_TALKING = 1

class Player(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x - 12,
            y - 12,
            24, 24
        )
        self.direction = [0,0]
        self.stepped_a_bit = False
        self.reset_last_position()
        self.step_action_threshold = 32
    
    def reset_last_position(self) -> None:

        self.last_checked_position = (self.rect.x, self.rect.y)
    
    def move(self, amount: tuple[float]) -> None:

        self.direction = amount

        dx,dy = amount
        self.rect.x = self.rect.x + dx
        self.rect.y = self.rect.y + dy

        dx = abs(self.rect.x - self.last_checked_position[0])
        dy = abs(self.rect.y - self.last_checked_position[1])

        self.stepped_a_bit = dx + dy > self.step_action_threshold
    
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

class Villager(pg.sprite.Sprite):

    def __init__(self, x: float, y: float, dialogue_filename: str):
        super().__init__()
        self.rect = pg.Rect(
            x - 12,
            y - 12,
            24, 24
        )
        self.direction = [0,0]
        self.dialogue_filename = dialogue_filename
        self.action_t = 0
        self.action_t_max = 0
        self.choose_action()
    
    def choose_action(self) -> None:

        self.direction = DIRECTIONS[random.choice(NPC_DIRECTIONS)]
        self.action_t = 0
        self.action_t_max = random.randint(15, 180)
    
    def speak(self) -> str:

        lines = []
        with open(self.dialogue_filename, "r") as file:

            line = file.readline()
            while line:
                line = line.replace("\n", "")
                if line:
                    lines.append(line)
                line = file.readline()
        
        return random.choice(lines)
    
    def move(self, amount: tuple[float]) -> None:

        self.action_t += 1
        if self.action_t >= self.action_t_max:
            self.choose_action()

        dx,dy = amount
        self.rect.x = self.rect.x + dx
        self.rect.y = self.rect.y + dy
    
    def get_rect(self) -> pg.Rect:
        return self.rect
    
class GameLogic:

    def __init__(self):

        self.terrain = {
            TERRAIN_GROUND: pg.sprite.Group(),
            TERRAIN_RADIATED_GROUND: pg.sprite.Group(),
            TERRAIN_BLOCKED: pg.sprite.Group()
        }
        self.villagers = pg.sprite.Group()
        self.transient_state = pg.sprite.Group()

        self.player = Player(320, 240)

        self.reset_state()
        self.mode = MODE_WALKING
        self.line = ""
    
    def reset_state(self) -> None:
        
        for sprite in self.transient_state.sprites():
            sprite.kill()
        
        self.reset_party_state()
        
    def reset_party_state(self) -> None:

        self.party_leader: model.Character = None
        self.inventory = {}

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
                elif line == "interactibles":
                    line = self.load_interactible_data(file)
                elif line == "member":
                    line = self.load_member_data(file)
                elif line == "inventory":
                    line = self.load_inventory_data(file)
                else:
                    raise Exception("Unkown header!")

    def load_member_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        new_member = model.Character()
        old_member = self.party_leader
        new_member.set_next(old_member)
        self.party_leader = new_member

        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            property, _, value = str.partition(line, ":")

            if property == "name":
                new_member.set_name(value)
            elif property == "type":
                if value == "soldier":
                    member_type = model.SOLDIER
                elif value == "mage":
                    member_type = model.MAGE
                else:
                    raise Exception(f"Unknown member type: {property}")
                new_member.set_type(member_type)
            elif property == "hp":
                new_member.set_hp(int(value))
            elif property == "max_hp":
                new_member.set_hp_max(int(value))
            elif property == "mp":
                new_member.set_mp(int(value))
            elif property == "max_mp":
                new_member.set_mp_max(int(value))
            else:
                raise Exception(f"Unknown property: {property}")

            line = file.readline()
        
        return ""
    
    def load_inventory_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            item, _, quantity = str.partition(line, ":")

            if item == "potion":
                item_type = model.HP_POTION
            elif item == "magic_draught":
                item_type = model.MP_POTION
            elif item == "bones":
                item_type = model.BONES
            else:
                raise Exception(f"Unknown item: {item}")

            self.inventory[item_type] = int(quantity)

            line = file.readline()
        
        return ""
    
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
    
    def load_interactible_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            object, _, arguments = str.partition(line, "(")
            arguments,_,_ = str.partition(arguments, ")")
            arguments = arguments.replace(" ", "")
            arguments = arguments.split(",")

            if object == "npc":
                new_npc = Villager(float(arguments[0]), float(arguments[1]), arguments[2])
                self.villagers.add(new_npc)
                self.transient_state.add(new_npc)
            else:
                raise Exception(f"Unknown class: {object}")

            line = file.readline()
        
        return ""

    def player_can_move(self) -> bool:

        hit_blocks = pg.sprite.spritecollide(
            sprite = self.player, 
            group = self.terrain[TERRAIN_BLOCKED], 
            dokill = False
        )
        if len(hit_blocks) != 0:
            return False

        hit_blocks = pg.sprite.spritecollide(
            sprite = self.player, 
            group = self.villagers, 
            dokill = False
        )
        return len(hit_blocks) == 0
    
    def npc_can_move(self, npc: Villager) -> bool:

        hit_blocks = pg.sprite.spritecollide(
            sprite = npc, 
            group = self.terrain[TERRAIN_BLOCKED], 
            dokill = False
        )
        if len(hit_blocks) != 0:
            return False
        
        hit_blocks = pg.sprite.spritecollide(
            sprite = npc, 
            group = self.terrain[TERRAIN_RADIATED_GROUND], 
            dokill = False
        )
        if len(hit_blocks) != 0:
            return False

        return not npc.rect.colliderect(self.player.rect)

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

    def make_player_interact(self)-> None:

        dx = 24 * self.player.direction[0]
        dy = 24 * self.player.direction[1]
        interaction_rect = self.player.rect.move(dx, dy)
    
        for villager in self.villagers.sprites():
            if villager.rect.colliderect(interaction_rect):
                villager.direction = [0,0]
                self.line = villager.speak()
                self.mode = MODE_TALKING
                return
    
    def update(self) -> int:

        for villager in self.villagers.sprites():
            direction = villager.direction
            villager.move(direction)
            if not self.npc_can_move(villager):
                direction[0] *= -1
                direction[1] *= -1
                villager.move(direction)
                villager.choose_action()
        
        if self.player.stepped_a_bit \
            and self.on_ground(self.player, self.terrain[TERRAIN_RADIATED_GROUND]):

            self.player.reset_last_position()
            chance = random.random()
            if chance > 0.5:
                monsters = self.generate_monsters()
                self.save_battle_data(monsters)
                return model.RETURN_ACTION_START_BATTLE
        
        return model.RETURN_ACTION_CONTINUE
    
    def on_ground(self,
        character: pg.sprite.Sprite,
        group: pg.sprite.Group) -> bool:

        hit_blocks = pg.sprite.spritecollide(character, group, False)

        return len(hit_blocks) > 0
    
    def generate_monsters(self) -> list[str]:

        monster_types = ("rat", "rat", "cultist")
        monster_count = random.randint(1,4)
        monsters = []
        for _ in range(monster_count):
            monsters.append(random.choice(monster_types))
        return monsters
    
    def save_battle_data(self, monsters: list[str]) -> None:

        with open("battle_data.txt", "w") as file:

            self.save_monster_data(file, monsters)
            self.save_party_data(file)
            self.save_inventory_data(file)
    
    def save_monster_data(self, 
        file: io.TextIOWrapper,
        monsters: list[str]) -> None:

        file.write("[enemies]\n")

        for monster_type in monsters:
            file.write(f"{monster_type}\n")

    def save_party_data(self, 
        file: io.TextIOWrapper) -> None:

        member = self.party_leader
        while member is not None:
            file.write("[member]\n")

            file.write(f"name: {member.name}\n")
            if member.type == model.SOLDIER:
                file.write("type: soldier\n")
            else:
                file.write("type: mage\n")
            file.write(f"hp: {member.hp}\n")
            file.write(f"max_hp: {member.hp_max}\n")
            file.write(f"mp: {member.mp}\n")
            file.write(f"max_mp: {member.mp_max}\n")
            
            member = member.next
    
    def save_inventory_data(self,
        file: io.TextIOWrapper) -> None:

        file.write("[inventory]\n")

        for (item_type, quantity) in self.inventory.items():
            file.write(f"{model.ITEM_DESCRIPTORS[item_type]}: {quantity}\n")
        
    def get_villagers(self) -> pg.sprite.Group:
        return self.villagers

    def get_mode(self) -> int:
        return self.mode
    
    def set_mode(self, mode: int) -> None:
        self.mode = mode
    
    def get_line(self) -> str:
        return self.line

game_context = GameLogic()