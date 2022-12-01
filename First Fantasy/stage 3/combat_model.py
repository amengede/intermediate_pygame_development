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

HP_POTION = 0
MP_POTION = 1
BONES = 2

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
    
class GameLogic:

    def __init__(self):

        self.reset_state()
    
    def reset_state(self) -> None:
        
        self.party_leader = None
        self.enemy_leader = None
        self.inventory = {}

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

game_context = GameLogic()