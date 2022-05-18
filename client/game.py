from typing import Dict, List
from client import Client
import pygame
import os

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE
)
from message import CREATION, LOCATION, REMOVE, Message
from message import REGISTER

from player import Player
from bullet import Bullet

from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from threading import Thread
import math

from entity import BULLET, PLAYER, Entity

class Game:
    
    def __init__(self):
        pygame.init()
        
        self.client = Client()
        self.register()
                
        # Setup the clock for a decent framerate
        self.clock = pygame.time.Clock()

        self.bullets: List[Bullet] = list()
        self.sprites = pygame.sprite.Group()
        
        # Set up the drawing window
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        
        self.player = None
        
        
        self.udp: Thread = Thread(target=self.connect)
        self.udp.start()
        
    def connect(self):
        self.entities: Dict[Entity] = {}        
        
        while True:
            message = self.client.receive()
            
            message_type = message.read_int()
            #print(f"Received message type {message_type}")
            
            if message_type == CREATION:
                entity_id = message.read_int()
                client_id = message.read_int()
                entity_type = message.read_int()
                x = message.read_float()
                y = message.read_float()
                
                if entity_type == PLAYER:
                    if self.player is None:
                        print(f"You are player #{client_id} entity #{entity_id} at x={x} y={y}")
                        entity = Player(self.client, client_id, entity_id, x, y)
                        self.sprites.add(entity)
                        self.player = entity
                    else:
                        print(f"Create other player #{entity_id} at x={x} y={y}")
                        entity = Player(self.client, client_id, entity_id, x, y, controllable=False)
                        self.sprites.add(entity)
                        
                        self.entities[entity_id] = entity   
                        
                elif entity_type == BULLET:
                    xSpeed = message.read_float()
                    ySpeed = message.read_float()
                    
                    entity = Bullet(entity_id, (x, y), xSpeed, ySpeed)
                    self.sprites.add(entity)
                    self.entities[entity_id] = entity
                    
                    if client_id == self.player.client_id:
                        self.bullets.append(entity)
                    print("Create a bullet #", entity_id, x, y)
                else:
                    print("Unknown client_type", entity_type)
                    continue   
                
            elif message_type == REMOVE:
                entity_id = message.read_int()
                other = self.entities[entity_id]
                self.sprites.remove(other)
                del self.entities[entity_id]
                print(f"Remove Client #{entity_id}")
            elif message_type == LOCATION:
                entity_id = message.read_int()
                x = message.read_float()
                y = message.read_float()
                
                if entity_id in self.entities:
                    other = self.entities[entity_id]
                    other.rect.x = x
                    other.rect.y = y
                else:
                    print("Could not move other player #" + str(entity_id))
        
    def register(self):
        message = Message()
        message.add_int(REGISTER)
        message.add_int(PLAYER)
        self.client.send(message)

    def loop(self):
        self.running = True
        try:
            while self.running:                
                self.update()
                self.draw()
                
                # Flip the display
                pygame.display.flip()

                self.clock.tick(30)
        finally:
            #print(f"Remove this Player #{self.entity_id}")
            message = Message()
            message.add_int(REMOVE)
            message.add_int(self.player.entity_id)
            self.client.send(message)
            
            for bullet in self.bullets:
                message = Message()
                message.add_int(REMOVE)
                message.add_int(bullet.entity_id)
                self.client.send(message)
                self.bullets.remove(bullet)
            
        pygame.quit()        
        os._exit(0)
    
    def _shoot(self):
        x, y = pygame.mouse.get_pos()
        
        pressed_keys = pygame.key.get_pressed()
        
        # Move the sprite based on user keypresses
        if pressed_keys[K_SPACE]:
            xSpeed = x - self.player.rect.x 
            ySpeed = y - self.player.rect.y
            distance = math.sqrt(xSpeed**2 + ySpeed**2)
            xSpeed /= distance
            ySpeed /= distance
            
            message = Message()
            message.add_int(REGISTER)
            message.add_int(BULLET)
            message.add_int(self.player.entity_id)
            message.add_float(self.player.rect.centerx)
            message.add_float(self.player.rect.centery)
            message.add_float(xSpeed)
            message.add_float(ySpeed)
            
            self.client.send(message)
        
    def update(self): 
        if self.player is None: return
         
        self._shoot()
        
        
        self.player.update()
        
        self.running = self.player.is_alive
        
        for bullet in self.bullets:
            bullet.update()
            
            message = Message()
            message.add_int(LOCATION)
            message.add_int(self.player.client_id)
            message.add_int(bullet.entity_id)
            message.add_float(bullet.rect.x)
            message.add_float(bullet.rect.y)
            self.client.send(message)
            
            if not bullet.alive():
                message = Message()
                message.add_int(REMOVE)
                message.add_int(bullet.entity_id)
                self.client.send(message)
                self.bullets.remove(bullet)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

            # Add a new enemy?
            """
            elif event.type == ADDENEMY:
                # Create the new enemy and add it to sprite groups
                new_enemy = Enemy()
                self.enemies.add(new_enemy)
                self.sprites.add(new_enemy)
            """

    def draw(self):
        # Fill the background black
        self.screen.fill((0, 0, 0))

        # Draw all sprites
        for entity in self.sprites:
            self.screen.blit(entity.surf, entity.rect)