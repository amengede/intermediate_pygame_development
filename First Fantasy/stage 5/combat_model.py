from __future__ import annotations
from config import *
import io

SOLDIER = 0
MAGE = 1
RAT = 2
CULTIST = 3

HP_GENERATORS = {
    RAT: {
        "low": 4,
        "high": 8
    },

    CULTIST: {
        "low": 8,
        "high": 16
    },
}

DAMAGE_GENERATORS = {
    SOLDIER: {
        "low": 12,
        "high": 16
    },

    MAGE: {
        "low": 4,
        "high":12
    },

    RAT: {
        "low": 1,
        "high": 4
    },

    CULTIST: {
        "low": 4,
        "high":6
    }
}

HP_POTION = 0
MP_POTION = 1
BONES = 2
ITEM_NAMES = {
    HP_POTION: "Health Potion",
    MP_POTION: "Magic Draught"
}

MODE_ACTION_SELECT = 0
MODE_ENEMY_SELECT = 1
MODE_SPELL_SELECT = 2
MODE_ITEM_SELECT = 3
MODE_MEMBER_ATTACK = 4
MODE_ENEMY_ATTACK = 5
MODE_MEMBER_SELECT = 6

ACTION_ATTACK = 0
ACTION_HARM_SPELL = 1
ACTION_HEAL_SPELL = 2
ACTION_USE_HP_POTION = 3
ACTION_USE_MP_POTION = 4

class Character:

    def __init__(self):
        self.next = None
        self.hp = 0
        self.hp_max = 0
        self.mp = 0
        self.mp_max = 0
        self.type = -1
        self.name = ""
    
    def set_next(self, next: Character) -> None:
        self.next = next
    
    def get_next(self) -> Character:
        return self.next
    
    def get_hp(self) -> int:
        return self.hp
    
    def set_hp(self, hp: int) -> None:
        self.hp = hp
    
    def change_hp(self, amount: int) -> None:
        self.hp = min(self.hp_max, max(0, self.hp + amount))
    
    def get_hp_max(self) -> int:
        return self.hp_max
    
    def set_hp_max(self, hp_max: int) -> None:
        self.hp_max = hp_max
    
    def get_mp(self) -> int:
        return self.mp
    
    def set_mp(self, mp: int) -> None:
        self.mp = mp
    
    def change_mp(self, amount: int) -> None:
        self.mp = min(self.mp_max, max(0, self.mp + amount))

    def get_mp_max(self) -> int:
        return self.mp_max
    
    def set_mp_max(self, mp_max: int) -> None:
        self.mp_max = mp_max

    def get_type(self) -> int:
        return self.type
    
    def set_type(self, type: int) -> None:
        self.type = type

    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        self.name = name
    
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
    
class GameLogic:

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
            
            new_enemy = Character()
            old_enemy = self.enemy_leader
            new_enemy.set_next(old_enemy)
            self.enemy_leader = new_enemy
            hp = random.randint(
                HP_GENERATORS[enemy_type]["low"],
                HP_GENERATORS[enemy_type]["high"]
            )
            new_enemy.set_hp(hp)
            new_enemy.set_hp_max(hp)
            new_enemy.set_name(name)
            new_enemy.set_type(enemy_type)

            line = file.readline()
        
        return ""
    
    def load_member_data(self, file: io.TextIOWrapper) -> str:

        line = file.readline()
        new_member = Character()
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
                    member_type = SOLDIER
                elif value == "mage":
                    member_type = MAGE
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

    def get_enemy_leader(self) -> Character:
        return self.enemy_leader
    
    def get_party_leader(self) -> Character:
        return self.party_leader
    
    def get_inventory(self) -> dict[int, int]:
        return self.inventory

    def first_valid_member(self, leader: Character) -> int:
        
        i = 0
        member = leader

        while member is not None:
            if member.get_hp() > 0:
                return i
            member = member.next
            i += 1
        return i
    
    def next_valid_member(self, leader: Character, current_index: int, search_direction: int) -> int:

        next_member = (current_index + search_direction) % leader.size()
        if leader.at(next_member).get_hp() == 0:
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
                and self.party_leader.at(self.current_character).get_mp() > 0:
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

    def get_mode(self) -> int:
        return self.mode
    
    def get_actions(self) -> list[str]:
        return self.actions

    def get_selected_action(self) -> int:
        return self.current_action
    
    def next_turn(self) -> None:

        if self.mode == MODE_ENEMY_ATTACK:
            if self.current_character + 1 == self.enemy_leader.size():
                self.selected_character = -1
                self.current_character = self.first_valid_member(self.party_leader)
                self.mode = MODE_ACTION_SELECT
            else:
                self.current_character += 1
                if self.enemy_leader.at(self.current_character).get_hp() == 0:
                    self.next_turn()
        
        else:
            if self.current_character + 1 == self.party_leader.size():
                self.selected_character = -1
                self.current_character = self.first_valid_member(self.enemy_leader)
                self.mode = MODE_ENEMY_ATTACK
            else:
                self.current_character += 1
                if self.party_leader.at(self.current_character).get_hp() == 0:
                    self.next_turn()
                else:
                    self.mode = MODE_ACTION_SELECT

    def has_won(self) -> bool:

        enemy = self.enemy_leader
        while enemy is not None:
            if enemy.get_hp() > 0:
                return False
            enemy = enemy.get_next()
        return True
    
    def has_lost(self) -> bool:

        member = self.party_leader
        while member is not None:
            if member.get_hp() > 0:
                return False
            member = member.get_next()
        return True
    
    def member_act(self) -> None:

        party_member = self.party_leader.at(self.current_character)

        if self.next_action == ACTION_ATTACK:
            target = self.enemy_leader.at(self.selected_character)
            damage = random.randint(
                DAMAGE_GENERATORS[party_member.get_type()]["low"],
                DAMAGE_GENERATORS[party_member.get_type()]["high"]
            )
            target.change_hp(-damage)
        
        elif self.next_action == ACTION_HARM_SPELL:
            target = self.enemy_leader.at(self.selected_character)
            damage = random.randint(12, 24)
            target.change_hp(-damage)
            cost = random.randint(4,6)
            party_member.change_mp(-cost)

        elif self.next_action == ACTION_HEAL_SPELL:
            target = self.party_leader.at(self.selected_character)
            hp_increase = random.randint(12, 24)
            target.change_hp(hp_increase)
            cost = random.randint(4,6)
            party_member.change_mp(-cost)

        elif self.next_action == ACTION_USE_HP_POTION:
            target = self.party_leader.at(self.selected_character)
            hp_increase = random.randint(12, 24)
            target.change_hp(hp_increase)
            self.inventory[HP_POTION] -= 1
            if self.inventory[HP_POTION] <= 0:
                self.inventory.pop(HP_POTION)
            
        elif self.next_action == ACTION_USE_MP_POTION:
            target = self.party_leader.at(self.selected_character)
            mp_increase = random.randint(6, 12)
            target.change_mp(mp_increase)
            self.inventory[MP_POTION] -= 1
            if self.inventory[MP_POTION] <= 0:
                self.inventory.pop(MP_POTION)
    
    def enemy_act(self) -> None:

        enemy = self.enemy_leader.at(self.current_character)
        if enemy is None:
            self.next_turn()
            return

        target = self.party_leader
        i = 0
        targets = []
        while target is not None:
            if target.get_hp() != 0:
                targets.append(i)
            target = target.get_next()
            i += 1
        
        self.selected_character = random.choice(targets)
        target = self.party_leader.at(self.selected_character)
        damage = random.randint(
            DAMAGE_GENERATORS[enemy.get_type()]["low"],
            DAMAGE_GENERATORS[enemy.get_type()]["high"]
        )
        target.change_hp(-damage)

    def update(self):

        if self.mode == MODE_MEMBER_ATTACK and self.t == 0:
            self.member_act()
        
        elif self.mode == MODE_ENEMY_ATTACK and self.t == 0:
            self.enemy_act()
        
        if self.mode == MODE_MEMBER_ATTACK \
            or self.mode == MODE_ENEMY_ATTACK:

            self.t += 1
            if self.t >= 60:
                self.t = 0
                self.next_turn()
    
game_context = GameLogic()