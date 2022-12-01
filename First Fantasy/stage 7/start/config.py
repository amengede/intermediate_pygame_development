import pygame as pg
import pygame.freetype as fontLib
import random
from collections.abc import Callable
import math

SCREEN_SIZE = (640, 480)

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