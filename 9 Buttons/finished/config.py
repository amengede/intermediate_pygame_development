import pygame as pg
import pygame.freetype as fontLib
import random
from collections.abc import Callable

BLOCK_STATUS_INACTIVE = 0
BLOCK_STATUS_ACTIVE = 1
SCREEN_SIZE = (640, 480 + 192)