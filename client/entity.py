import pygame
from abc import ABC, abstractmethod


PLAYER = 1
BULLET = 2

class Entity(pygame.sprite.Sprite, ABC):
    
    @abstractmethod
    def update(self, *args, **kwars):
        pass
    
    