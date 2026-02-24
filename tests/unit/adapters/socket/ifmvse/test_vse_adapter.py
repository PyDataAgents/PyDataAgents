import os
import struct
import time
import socket
import pytest


from pydag.adapters.socket.ifmvse.VSEAdapter import VSEAdapter, Messages
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.plot.PlotlifyService import PlotlifyService


@pytest.mark.skip("only test if vse device is running")
def test_vse_adapter():
    
    vse = VSEAdapter(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 10000)
    
    vse.install()
    assert vse.connect(), "Could not connect to vse device"
    
    buf = ListBuffer(capacity=100000)
    buffers = buf.to_dict()
    
    vse.subscribe(buffers, [], 0, 0)
    
    time.sleep(10)
    
    vse.unsubscribe()
    
    vse.disconnect()
    
    vse.uninstall()
    
    print(buf.data())
    
    file_path = os.path.dirname(__file__) + os.sep + "test_plotly_vse_adapter.html"
    PlotlifyService.line(y=buf.data()["values"]).to_file(file_path)
    
    
@pytest.mark.skip("only test interactively")  
def test_vse_raw_socket():
    sock : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    sock.connect(("192.168.0.10", 3321))
    
    n = 2
    while n > 0:
        bs = sock.recv(2)
        n = len(bs)
        
    sock.close()

@pytest.mark.skip("only test interactively")     
def test_vse_single_messages():
    
    vse = VSEAdapter(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 10000)
    
    vse.install()
    assert vse.connect(), "Could not connect to vse device"
    
    vse._set_mode(1)
    
    bs = vse._socket.recv(Messages.MSG_ACK.value.n)
    d = struct.unpack(Messages.MSG_ACK.value.sch, bs)
    
    print(d)