from typing import Union
import socket

from message import Message


class Client(socket.socket):
    def __init__(self, host="127.0.0.1", port=20001) -> None:
        super().__init__(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.serverAddressPort = (host, port)
        #self.setblocking(False)
    
    def send(self, msg: Union[bytes, Message]):
        if type(msg) == Message:
            msg = msg.data
        self.sendto(msg, self.serverAddressPort)
        
    def receive(self, bufferSize = 1024) -> Message:
        message, _ = self.recvfrom(bufferSize)
        #print("Receive message with length:", len(message))
        #print(message)
        return Message(message)
