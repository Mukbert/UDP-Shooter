import __future__

import random 
import pygame
from message import LOCATION, Message
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
from typing import Tuple
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from entity import Entity
import math

# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Bullet(Entity):
    def __init__(self, entity_id: int, center: Tuple[float, float], xSpeed: float, ySpeed: float):
        super(Bullet, self).__init__()
        
        self.entity_id = entity_id
        self.xSpeed = xSpeed
        self.ySpeed = ySpeed
        angle = -math.degrees(math.atan2(ySpeed, xSpeed))
                
        self.surf = pygame.image.load("res/missle.png").convert()
        self.surf = pygame.transform.rotate(self.surf, angle)
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=center)
        self.speed = random.randint(10, 16)
    
    def update(self):
        # Move the sprite based on speed
        self.rect.move_ip(self.xSpeed * self.speed, self.ySpeed * self.speed)
        
        # Remove the sprite when it passes the left edge of the screen
        if self.rect.right < 0 or self.rect.right > SCREEN_WIDTH or \
            self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.kill()