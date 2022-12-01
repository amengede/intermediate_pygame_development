from __future__ import annotations

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
ITEM_DESCRIPTORS = {
    HP_POTION: "potion",
    MP_POTION: "magic_draught",
    BONES: "bones"
}

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_START_BATTLE = 1
RETURN_ACTION_RETURN_TO_ADVENTURE = 2
RETURN_ACTION_GAME_END = 3

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