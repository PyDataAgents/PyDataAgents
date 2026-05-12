import struct

import numpy as np

from pydag.services.socket.ByteStreamService import ByteStreamService
from pydag.services.socket.SerialService import SerialService
from pydag.services.socket.TCPClientService import TCPClientService

def test_000():
    schema = '=bh5s'
    record_size = struct.calcsize(schema)
    print(f"Record size: {record_size} bytes")
    data = b'\x01\x10\x00\x68\x65\x6c\x6c\x6f' * 3  # 3 records
    print(len(data))
    samples = [
        struct.unpack(schema, data[i : i + record_size])
        for i in range(0, len(data), record_size)
    ]
    result = []
    for v in samples:
        if isinstance(v, (bytes, bytearray)):
            v = v.decode("utf-8").rstrip('\x00')  # remove null padding
        result.append(v)    
    
    print(result)
    
    
def test_010():
    
    schema = "=fid"
    ba = TCPClientService()
    d = (12.0, 1, 4.7)
    
    b = ba._encode(schema, d)
    print(b)    
    
    rd = ba._decode(schema, b)
    print(rd)
    
    
def test_020():
    schema = "=fid"    
    bn, fn = ByteStreamService.decode_schema(schema)
    print(f"Bytes: {bn}, Fields: {fn}")
    
def test_021():
    schema = "fid5siii"    
    bn, fn = ByteStreamService.decode_schema(schema)
    print(f"Bytes: {bn}, Fields: {fn}")
    
def test_030():
    data = "12.5;3;89"
    schema = "=fii"
    tu = tuple(data.split(";"))
    print(tu)    
    tu_forced = ByteStreamService.force_schema(schema, tu)
    print(tu_forced)

def test_031():
    line = "12.5;3;89"
    
    tu = tuple(line.split(";"))
    print(list(tu))
    
    schema = "=fii"
    tu_forced = ByteStreamService.force_schema(schema, tu)
    
    sa = SerialService()
    encoded = sa._encode(schema, tu_forced)
    print(encoded)
    
    decoded = sa._decode(schema, encoded)
    print(decoded)  
    
    
