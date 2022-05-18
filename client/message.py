from __future__ import annotations

import struct

REGISTER = 1
LOCATION = 2
CREATION = 3
REMOVE = 4

class Message():
    def __init__(self, data: bytes = None) -> None:
        if data is None:
            self.data = bytearray()
        else:
            self.data = bytearray(data)
        self.pointer = 0

    def add_int(self, i: int, size: int=2) -> Message:
        b = i.to_bytes(size, byteorder='big')
        self.data.extend(b)
        return self
    
    def read_int(self, size: int = 2) -> int:
        b = self.data[self.pointer : self.pointer + size]
        i = int.from_bytes(b, byteorder='big', signed=True)
        self.pointer += size
        return i
        
    def add_float(self, f: float) -> Message:
        b = bytearray(struct.pack('f', f))
        self.data.extend(b)
        return self
    
    def read_float(self) -> int:
        i, = struct.unpack('f', self.data[self.pointer: self.pointer + 4])
        self.pointer += 4
        return i