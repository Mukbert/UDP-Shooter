import socket
import random
import os
from typing import Set
from entity import BULLET, PLAYER, EntityData, creation_message, location_message

from message import CREATION, REGISTER, LOCATION, REMOVE, Message


class Server(socket.socket):
    def __init__(self, host="127.0.0.1", port=20001) -> None:
        super().__init__(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.bind((host, port))
        
        print("UDP server up and listening") 
        
    def receive(self, bufferSize = 1024):
        return self.recvfrom(bufferSize)
    
class ClientHandler():
    
    COUNTER: int = 0
    
    def __init__(self, entity: EntityData, server, address) -> None:
        self.entity = entity
        self.server = server
        self.address = address
        
        ClientHandler.COUNTER += 1
        self.client_id = ClientHandler.COUNTER
            
    def send(self, message: Message):
        #print("Send message with length:", len(message.data))
        self.server.sendto(message.data, self.address)   
    

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def main():
    server = Server()
    
    clients: dict[int, ClientHandler] = {}
    entities: dict[int, EntityData] = {}
    
    deamons: Set[int] = set()
    
    ENTITY_COUNTER = 0
    
    while(True):

        message, address  = server.receive()
        
        message = Message(message)
        message_type = message.read_int()
        
        
        if message_type == REGISTER:
            # increase entity counter for every new registration
            
            ENTITY_COUNTER += 1
            entity_id = ENTITY_COUNTER
            
            entity_type = message.read_int()
            
            entity = EntityData()
            entity.entity_id = entity_id
            entity.type = entity_type
            entities[entity_id] = entity
            
            if entity_type == PLAYER:
                # create client
                client = ClientHandler(entity, server, address)
                clients[client.client_id] = client
                 
                entity.client_id = client.client_id
                entity.x = random.randint(0, SCREEN_WIDTH)
                entity.y = random.randint(0, SCREEN_HEIGHT)
                print(f"Create Player #{entity.client_id} entity #{entity.entity_id} at x={entity.x} y={entity.y}")
            
            elif entity_type == BULLET:
                entity.client_id = message.read_int()
                entity.x = message.read_float()
                entity.y = message.read_float()
                entity.xSpeed = message.read_float()
                entity.ySpeed = message.read_float()
                print(f"Create Bullet #{entity.entity_id} at x={entity.x} y={entity.y}")
                
                client = clients[entity.client_id]
            
            # send creation message back to understand own position and its id
            message = creation_message(entity)
            client.send(message)
            
            for other_entity in entities.values():
                if client.client_id == other_entity.client_id: continue
                
                # let new client know about all other players
                other_message = creation_message(other_entity)
                client.send(other_message)
                
                try:
                    # let other client know about new client
                    other_client = clients[other_entity.client_id]
                    client_message = creation_message(entity)
                    other_client.send(client_message)
                except:
                    deamons.append(entity.client_id)
                    
            
            
        elif message_type == LOCATION:
            # decode message
            client_id = message.read_int()
            entity_id = message.read_int()
            x = message.read_float()
            y = message.read_float()
            
            if entity_id not in entities:
                print(f"Location: Entity #{entity_id} does not exist")
                continue
            
            # update client location
            entity = entities[entity_id]
            entity.x = x
            entity.y = y
            #print(f"Move Player #{client_id} to x={x} y={y}")
            
            # encode location into byte message
            message = location_message(entity)
            
            for other_client in clients.values():
                if client_id == other_client.client_id: continue

                try:
                     # let other client know about new client location
                    other_client.send(message)
                except:
                    deamons.add(other_client.client_id)
                    
        elif message_type == REMOVE:
            # decode message
            entity_id = message.read_int()
            entity = entities.pop(entity_id, None)
            
            if entity is None:
                print(f"Remove: Entity #{entity_id} does not exist")
                continue
            
            message = Message()
            message.add_int(REMOVE)
            message.add_int(entity_id)
            
            print(f"Remove Entity #{entity_id}")
            
            for client in clients.values():
                try:
                    # let other client know about new client location
                    client.send(message)
                except:
                    deamons.add(client.entity.entity_id)
            
        else:
            print("Unknown message!")
            
        for deamon_id in deamons:
            
            message = Message()
            message.add_int(REMOVE)
            message.add_int(deamon_id)
            
            clients.pop(deamon_id, None)
            for client in clients.values():
                try:
                    # let other client know about new client location
                    client.send(message)
                except:
                    deamons.add(client.client_id)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os._exit(0)
    