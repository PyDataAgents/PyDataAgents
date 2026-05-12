
import time

import pytest
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.socket.ByteStreamService import ByteStreamService
from pydag.services.socket.SerialService import SerialService


def test_000():   
    com_port = "COM4"
    schema = "=fff"
    sa = SerialService(host=com_port, baud_rate=9600, new_line_mode=False, read_byte_schema=schema, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    
    sa.install()
    
    bn, fn = ByteStreamService.decode_schema(schema)
    
    for _ in range(10):
        bs = sa._receive(bn)    
        t = sa._decode(schema, bs)
        print(t)
        time.sleep(1.1)
        
    sa.uninstall()
