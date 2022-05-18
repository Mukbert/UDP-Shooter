from dataclasses import dataclass

from message import CREATION, LOCATION, Message


# Global constants
PLAYER = 1
BULLET = 2


@dataclass
class EntityData:
    entity_id: float = 0
    x: float = 0
    y: float = 0
    type: int = 0
    client_id: int = 0
    xSpeed: float = 0
    ySpeed: float = 0
        
def creation_message(entity: EntityData) -> Message:
    message = Message()
    message.add_int(CREATION)
    message.add_int(entity.entity_id)
    message.add_int(entity.client_id)
    message.add_int(entity.type)
    message.add_float(entity.x)
    message.add_float(entity.y) 
    if entity.type == BULLET:
        message.add_float(entity.xSpeed)
        message.add_float(entity.ySpeed) 
    
    return message 
    
def location_message(entity: EntityData) -> Message:
    message = Message()
    message.add_int(LOCATION)
    message.add_int(entity.entity_id)
    message.add_float(entity.x)
    message.add_float(entity.y) 
    return message
    