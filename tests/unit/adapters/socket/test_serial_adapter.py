
import time

import pytest
pytest.importorskip("serial")

from pydag.adapters.socket.ByteStreamAdapter import ByteStreamAdapter
from pydag.adapters.socket.SerialAdapter import SerialAdapter


@pytest.mark.skip(reason="for this test a serial device must be connected on specified COM port and adhere to the specified schema")
def test_000():   
    com_port = "COM4"
    schema = "=fff"
    sa = SerialAdapter(host=com_port, baud_rate=9600, new_line_mode=False, read_byte_schema=schema)
    
    sa.install()
    sa.connect()
    
    bn, fn = ByteStreamAdapter.decode_schema(schema)
    
    for _ in range(10):
        bs = sa._receive(bn)    
        t = sa._decode(schema, bs)
        print(t)
        time.sleep(1.1)
        
    sa.disconnect()
    sa.uninstall()
