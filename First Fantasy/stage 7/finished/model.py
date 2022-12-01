from __future__ import annotations
from config import *
import io

class Character:

    def __init__(self):
        self.next = None
        self.hp = 0
        self.hp_max = 0
        self.mp = 0
        self.mp_max = 0
        self.type = -1
        self.name = ""
    
    def change_hp(self, amount: int) -> None:
        self.hp = min(self.hp_max, max(0, self.hp + amount))
    
    def change_mp(self, amount: int) -> None:
        self.mp = min(self.mp_max, max(0, self.mp + amount))
    
    def size(self) -> int:
        
        i = 0
        member = self
        while member is not None:
            member = member.next
            i += 1
        
        return i

    def at(self, position: int) -> Character:
        
        i = 0
        member = self
        while i < position:
            member = member.next
            i += 1
        
        return member

class PartyMember(Character):

    def act(self) -> None:

        environment = game_context["combat"]
        if environment.next_action == ACTION_ATTACK:
            target = environment.enemy_leader.at(environment.selected_character)
            damage = random.randint(
                DAMAGE_GENERATORS[self.type]["low"],
                DAMAGE_GENERATORS[self.type]["high"]
            )
            target.change_hp(-damage)
        
        elif environment.next_action == ACTION_HARM_SPELL:
            target = environment.enemy_leader.at(environment.selected_character)
            damage = random.randint(12, 24)
            target.change_hp(-damage)
            cost = random.randint(4,6)
            self.change_mp(-cost)

        elif environment.next_action == ACTION_HEAL_SPELL:
            target = environment.party_leader.at(environment.selected_character)
            hp_increase = random.randint(12, 24)
            target.change_hp(hp_increase)
            cost = random.randint(4,6)
            self.change_mp(-cost)

        elif environment.next_action == ACTION_USE_HP_POTION:
            target = environment.party_leader.at(environment.selected_character)
            hp_increase = random.randint(12, 24)
            target.change_hp(hp_increase)
            environment.inventory[HP_POTION] -= 1
            if environment.inventory[HP_POTION] <= 0:
                environment.inventory.pop(HP_POTION)
            
        elif environment.next_action == ACTION_USE_MP_POTION:
            target = environment.party_leader.at(environment.selected_character)
            mp_increase = random.randint(6, 12)
            target.change_mp(mp_increase)
            environment.inventory[MP_POTION] -= 1
            if environment.inventory[MP_POTION] <= 0:
                environment.inventory.pop(MP_POTION)

class EnemyPartyMember(Character):

    def act(self) -> None:

        environment = game_context["combat"]

        target = environment.party_leader
        i = 0
        targets = []
        while target is not None:
            if target.hp != 0:
                targets.append(i)
            target = target.next
            i += 1
        
        environment.selected_character = random.choice(targets)
        target = environment.party_leader.at(environment.selected_character)
        damage = random.randint(
            DAMAGE_GENERATORS[self.type]["low"],
            DAMAGE_GENERATORS[self.type]["high"]
        )
        target.change_hp(-damage)

class Human(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):

        super().__init__()

        self.rect = pg.Rect(
            x - 12,
            y - 12,
            24, 24
        )
        self.direction = [0,0]
        self.step = 0
        self.direction_descriptor = NONE
        self.speed = 0
    
    def move(self, amount: list[float]) -> None:

        self.speed = math.sqrt(amount[0] ** 2 + amount[1] ** 2)
        
        if amount[0] == 0:
            if amount[1] < 0:
                self.direction_descriptor = NORTH
            elif amount[1] > 0:
                self.direction_descriptor = SOUTH
        elif amount[0] < 0:
            if amount[1] < 0:
                self.direction_descriptor = NORTH_WEST
            elif amount[1] > 0:
                self.direction_descriptor = SOUTH_WEST
            else:
                self.direction_descriptor = WEST
        else:
            if amount[1] < 0:
                self.direction_descriptor = NORTH_EAST
            elif amount[1] > 0:
                self.direction_descriptor = SOUTH_EAST
            else:
                self.direction_descriptor = EAST

        dx,dy = amount
        self.rect.x = self.rect.x + dx
        self.rect.y = self.rect.y + dy
    
    def overlaps_with(self,
        group: pg.sprite.Group) -> bool:

        return len(
            pg.sprite.spritecollide(
                self, group, False
            )
        ) > 0

class Player(Human):

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.stepped_a_bit = False
        self.reset_last_position()
        self.step_action_threshold = 32
    
    def reset_last_position(self) -> None:

        self.last_checked_position = (self.rect.x, self.rect.y)
    
    def move(self, amount: tuple[float]) -> None:

        super().move(amount)

        self.direction = amount

        dx = abs(self.rect.x - self.last_checked_position[0])
        dy = abs(self.rect.y - self.last_checked_position[1])

        self.stepped_a_bit = dx + dy > self.step_action_threshold
    
    def can_move(self, 
        blocked_terrain: pg.sprite.Group, 
        villagers: pg.sprite.Group) -> bool:

        if self.overlaps_with(blocked_terrain):
            return False

        return not self.overlaps_with(villagers)

    def get_interraction_rect(self) -> pg.Rect:

        return pg.Rect(self.rect.x - 12, self.rect.y - 12, 48, 48)
    
class Block(pg.sprite.Sprite):

    def __init__(self, x: float, y: float):
        super().__init__()
        self.rect = pg.Rect(
            x,
            y,
            32, 32
        )

class Villager(Human):

    def __init__(self, x: float, y: float, dialogue_filename: str):
        
        super().__init__(x,y)

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

        super().move(amount)

        self.action_t += 1
        if self.action_t >= self.action_t_max:
            self.choose_action()
    
    def can_move(self, 
        blocked_terrain: pg.sprite.Group, 
        radiated_terrain: pg.sprite.Group, 
        player_rect: pg.Rect) -> bool:

        if self.overlaps_with(blocked_terrain):
            return False
        
        if self.overlaps_with(radiated_terrain):
            return False

        return not self.rect.colliderect(player_rect)
    
class GameLogic:

    def load_member_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        new_member = PartyMember()
        old_member = self.party_leader
        new_member.next = old_member
        self.party_leader = new_member

        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            property, _, value = str.partition(line, ":")

            if property == "name":
                new_member.name = value
            elif property == "type":
                if value == "soldier":
                    member_type = SOLDIER
                elif value == "mage":
                    member_type = MAGE
                else:
                    raise Exception(f"Unknown member type: {property}")
                new_member.type = member_type
            elif property == "hp":
                new_member.hp = int(value)
            elif property == "max_hp":
                new_member.hp_max = int(value)
            elif property == "mp":
                new_member.mp = int(value)
            elif property == "max_mp":
                new_member.mp_max = int(value)
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
                item_type = HP_POTION
            elif item == "magic_draught":
                item_type = MP_POTION
            elif item == "bones":
                item_type = BONES
            else:
                raise Exception(f"Unknown item: {item}")

            self.inventory[item_type] = int(quantity)

            line = file.readline()
        
        return ""
 
    def save_party_data(self, 
        file: io.TextIOWrapper) -> None:

        member = self.party_leader
        while member is not None:
            file.write("[member]\n")

            file.write(f"name: {member.name}\n")
            if member.type == SOLDIER:
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
            file.write(f"{ITEM_DESCRIPTORS[item_type]}: {quantity}\n")

class AdventureGameLogic(GameLogic):

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

        self.party_leader: Character = None
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
    
    def move_player(self, movement: list[float]) -> None:

        self.player.move(movement)
        if not self.player.can_move(
            self.terrain[TERRAIN_BLOCKED], 
            self.villagers):
            movement[0] *= -1
            movement[1] *= -1
            self.player.move(movement)
        elif self.player.speed > 0:
            self.player.step = (self.player.step + 0.25) % 3

    def make_player_interact(self)-> None:

        interaction_rect = self.player.get_interraction_rect()
    
        for villager in self.villagers.sprites():
            if villager.rect.colliderect(interaction_rect):
                dx = self.player.rect.x - villager.rect.x
                if dx != 0:
                    dx = dx/abs(dx)
                dy = self.player.rect.y - villager.rect.y
                if dy != 0:
                    dy = dy/abs(dy)
                villager.direction = [dx,dy] 
                self.line = villager.speak()
                self.mode = MODE_TALKING
                return
    
    def update(self) -> int:

        for villager in self.villagers.sprites():
            direction = villager.direction
            villager.move(direction)
            if not villager.can_move(
                self.terrain[TERRAIN_BLOCKED],
                self.terrain[TERRAIN_RADIATED_GROUND],
                self.player.rect):
                direction[0] *= -1
                direction[1] *= -1
                villager.move(direction)
                villager.choose_action()
            elif villager.speed > 0:
                villager.step = (villager.step + 0.25) % 3
        
        if self.player.stepped_a_bit \
            and self.player.overlaps_with(self.terrain[TERRAIN_RADIATED_GROUND]):

            self.player.reset_last_position()
            chance = random.random()
            if chance > 0.5:
                monsters = self.generate_monsters()
                self.save_battle_data(monsters)
                return RETURN_ACTION_START_BATTLE
        
        return RETURN_ACTION_CONTINUE
    
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

class CombatGameLogic(GameLogic):

    def __init__(self):

        self.reset_state()
        self.keypress_handlers = {
            MODE_ACTION_SELECT: self.handle_keypress_action_select,
            MODE_ENEMY_SELECT: self.handle_keypress_enemy_select,
            MODE_SPELL_SELECT: self.handle_keypress_spell_select,
            MODE_ITEM_SELECT: self.handle_keypress_item_select,
            MODE_MEMBER_SELECT: self.handle_keypress_member_select
        }

        self.actions = ("Attack", "Spell", "Item")
        self.items = []
        self.spells = ("Harm", "Heal")
        self.current_action = 0
        self.current_character = -1
        self.selected_character = -1
        self.next_action = -1
        self.t = 0
    
    def reset_state(self) -> None:
        
        self.party_leader = None
        self.enemy_leader = None
        self.inventory = {}
        self.mode = MODE_ACTION_SELECT

    def load_from_file(self, filename: str) -> None:
        
        with open(filename, mode = "r") as file:

            line = file.readline()
            while (line):

                if line[0] != "[":
                    raise Exception("Invalid line found")
                
                line = line.rstrip()[1:-1]

                if line == "enemies":
                    line = self.load_enemy_data(file)
                elif line == "member":
                    line = self.load_member_data(file)
                elif line == "inventory":
                    line = self.load_inventory_data(file)
                else:
                    raise Exception("Unkown header!")
            
            self.current_character = self.first_valid_member(self.party_leader)
    
    def load_enemy_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        while (line):

            if line[0] == "[":
                return line
            
            line = line.replace("\n", "")

            if line == "rat":
                enemy_type = RAT
                name = "Rat"
            elif line == "cultist":
                enemy_type = CULTIST
                name = "Cultist"
            else:
                raise Exception(f"Unknown enemy type: {line}")
            
            new_enemy = EnemyPartyMember()
            old_enemy = self.enemy_leader
            new_enemy.next = old_enemy
            self.enemy_leader = new_enemy
            hp = random.randint(
                HP_GENERATORS[enemy_type]["low"],
                HP_GENERATORS[enemy_type]["high"]
            )
            new_enemy.hp = hp
            new_enemy.hp_max = hp
            new_enemy.name = name
            new_enemy.type = enemy_type

            line = file.readline()
        
        return ""
    
    def save_battle_data(self) -> None:

        with open("party_data.txt", "w") as file:

            self.save_party_data(file)
            self.save_inventory_data(file)
    
    def first_valid_member(self, leader: Character) -> int:
        
        i = 0
        member = leader

        while member is not None:
            if member.hp > 0:
                return i
            member = member.next
            i += 1
        return i
    
    def next_valid_member(self, leader: Character, current_index: int, search_direction: int) -> int:

        next_member = (current_index + search_direction) % leader.size()
        if leader.at(next_member).hp == 0:
            return self.next_valid_member(leader, next_member, search_direction)
        return next_member
    
    def handle_keypress(self, event: pg.event.Event) -> None:

        self.keypress_handlers[self.mode](event)

    def handle_keypress_action_select(self, event: pg.event.Event) -> None:
        
        if event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
            self.current_action = (self.current_action + 1) % len(self.actions)
        
        elif event.key == pg.K_UP or event.key == pg.K_LEFT:
            self.current_action = (self.current_action - 1) % len(self.actions)
        
        elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
            if self.actions[self.current_action] == "Attack":
                self.mode = MODE_ENEMY_SELECT
                self.next_action = ACTION_ATTACK
                self.selected_character = self.first_valid_member(self.enemy_leader)
            elif self.actions[self.current_action] == "Spell" \
                and self.party_leader.at(self.current_character).mp > 0:
                self.mode = MODE_SPELL_SELECT
                self.current_action = 0
            elif self.actions[self.current_action] == "Item":

                self.items = []
                for (item_type, quantity) in self.inventory.items():
                    if item_type != BONES:
                        self.items.append(f"{ITEM_NAMES[item_type]}: {quantity}")
                
                self.mode = MODE_ITEM_SELECT
                self.current_action = 0

    def handle_keypress_enemy_select(self, event: pg.event.Event) -> None:
        
        if event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
            self.selected_character = self.next_valid_member(self.enemy_leader, self.selected_character, 1)
        
        elif event.key == pg.K_UP or event.key == pg.K_LEFT:
            self.selected_character = self.next_valid_member(self.enemy_leader, self.selected_character, -1)
        
        elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
            self.mode = MODE_MEMBER_ATTACK
            self.t = 0
        
        elif event.key == pg.K_ESCAPE:
            self.mode = MODE_ACTION_SELECT
            self.selected_character = -1

    def handle_keypress_spell_select(self, event: pg.event.Event) -> None:
        
        if event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
            self.current_action = (self.current_action + 1) % len(self.spells)
        
        elif event.key == pg.K_UP or event.key == pg.K_LEFT:
            self.current_action = (self.current_action - 1) % len(self.spells)
        
        elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
            if self.spells[self.current_action] == "Harm":
                self.mode = MODE_ENEMY_SELECT
                self.next_action = ACTION_HARM_SPELL
                self.selected_character = self.first_valid_member(self.enemy_leader)
            else:
                self.mode = MODE_MEMBER_SELECT
                self.next_action = ACTION_HEAL_SPELL
                self.selected_character = self.first_valid_member(self.party_leader)
        
        elif event.key == pg.K_ESCAPE:
            self.mode = MODE_ACTION_SELECT
            self.selected_character = -1
            self.current_action = 0

    def handle_keypress_item_select(self, event: pg.event.Event) -> None:
        
        if event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
            self.current_action = (self.current_action + 1) % len(self.items)
        
        elif event.key == pg.K_UP or event.key == pg.K_LEFT:
            self.current_action = (self.current_action - 1) % len(self.items)
        
        elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:

            item_to_use, _, _ = str.partition(self.items[self.current_action], ":")

            if item_to_use == "Health Potion":
                self.mode = MODE_MEMBER_SELECT
                self.next_action = ACTION_USE_HP_POTION
                self.selected_character = self.first_valid_member(self.party_leader)
            else:
                self.mode = MODE_MEMBER_SELECT
                self.next_action = ACTION_USE_MP_POTION
                self.selected_character = self.first_valid_member(self.party_leader)
        
        elif event.key == pg.K_ESCAPE:
            self.mode = MODE_ACTION_SELECT
            self.selected_character = -1
            self.current_action = 0

    def handle_keypress_member_select(self, event: pg.event.Event) -> None:
        
        if event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
            self.selected_character = self.next_valid_member(self.party_leader, self.selected_character, 1)
        
        elif event.key == pg.K_UP or event.key == pg.K_LEFT:
            self.selected_character = self.next_valid_member(self.party_leader, self.selected_character, -1)
        
        elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
            self.mode = MODE_MEMBER_ATTACK
            self.t = 0
        
        elif event.key == pg.K_ESCAPE:
            self.mode = MODE_ACTION_SELECT
            self.selected_character = -1
    
    def next_turn(self) -> None:

        if self.mode == MODE_ENEMY_ATTACK:
            if self.current_character + 1 == self.enemy_leader.size():
                self.selected_character = -1
                self.current_character = self.first_valid_member(self.party_leader)
                self.mode = MODE_ACTION_SELECT
            else:
                self.current_character += 1
                if self.enemy_leader.at(self.current_character).hp == 0:
                    self.next_turn()
        
        else:
            if self.current_character + 1 == self.party_leader.size():
                self.selected_character = -1
                self.current_character = self.first_valid_member(self.enemy_leader)
                self.mode = MODE_ENEMY_ATTACK
            else:
                self.current_character += 1
                if self.party_leader.at(self.current_character).hp == 0:
                    self.next_turn()
                else:
                    self.mode = MODE_ACTION_SELECT

    def all_dead(self, leader: Character) -> bool:

        member = leader
        while member is not None:
            if member.hp > 0:
                return False
            member = member.next
        return True
    
    def update(self) -> int:

        if self.mode == MODE_MEMBER_ATTACK and self.t == 45:
            member = self.party_leader.at(self.current_character)
            member.act()
        
        elif self.mode == MODE_ENEMY_ATTACK and self.t == 45:
            enemy = self.enemy_leader.at(self.current_character)
            if enemy is None:
                self.next_turn()
                return
            enemy.act()
        
        if self.mode == MODE_MEMBER_ATTACK \
            or self.mode == MODE_ENEMY_ATTACK:

            self.t += 1
            if self.t >= 60:

                if self.all_dead(self.party_leader):
                    return RETURN_ACTION_GAME_END
                if self.all_dead(self.enemy_leader):
                    self.save_battle_data()
                    return RETURN_ACTION_RETURN_TO_ADVENTURE
                self.t = 0
                self.next_turn()

        return RETURN_ACTION_CONTINUE

game_context = {
    "adventure": AdventureGameLogic(),
    "combat": CombatGameLogic()
}