import pygame
import sys
from pygame.locals import *

from preferences import off

class Pane:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Anish's chip-8")

        self.screen = pygame.Surface((64, 32))
        # self.screen = pygame.display.set_mode((64, 32), pygame.RESIZABLE)
        self.screen.fill(off)

    def clear_screen(self):
        self.screen.fill(off)
        pygame.display.update()