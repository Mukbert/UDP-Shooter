import pygame
from client import Client
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
)
from entity import Entity

# Define a Player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(Entity):
    def __init__(self, client: Client, client_id: int, entity_id: int, x: float, y: float, controllable: bool=True):
        super(Player, self).__init__()
        self.client = client
        self.client_id = client_id
        self.entity_id = entity_id
        self.controllable = controllable
        
        self.surf = pygame.image.load("res/player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(x=x, y=y)
        #self.rect.x = x
        #self.rect.y = y
        self.is_alive = True
        
        self.speed = 10

    def _move(self):
        pressed_keys = pygame.key.get_pressed()
        
        x_diff, y_diff = 0, 0
        # Move the sprite based on user keypresses
        if pressed_keys[K_UP]:
            y_diff -= self.speed
        if pressed_keys[K_DOWN]:
            y_diff += self.speed
        if pressed_keys[K_LEFT]:
            x_diff -= self.speed
        if pressed_keys[K_RIGHT]:
            x_diff += self.speed
            
        if x_diff != 0 or y_diff != 0:
            self.rect.x += x_diff
            self.rect.y += y_diff
                        
            # Keep player on the screen
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT  
            
            #print(f"Move Player #{self.entity_id} to x={self.rect.left} y={self.rect.top}")
            
            message = Message()
            message.add_int(LOCATION)
            message.add_int(self.client_id)
            message.add_int(self.entity_id)
            message.add_float(self.rect.x)
            message.add_float(self.rect.y)
            self.client.send(message)
    
    def update(self):
        if not self.controllable: return
        
        self._move()
               
        """  
        # Check if any enemies have collided with the player
        if pygame.sprite.spritecollideany(self, enemies):
            self.kill()
            self.is_alive = False
        """   