import os
import struct
import time
import socket


from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.socket.ifmvse.VSEService import VSEService, Messages
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.plot.PlotlifyService import PlotlifyService
from pydag.services.csv.CsvWriteService import CsvWriteService


def test_vse_adapter():
    
    buf = ListBuffer(capacity=100000)
    buf.install()
    vse = VSEService(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 10000, thread_type=ThreadType.DAEMON.value)
    vse.add_buffer(buf)
    vse.install()
    
    
    vse.subscribe()
    
    time.sleep(10)
    
    vse.unsubscribe()
        
    vse.uninstall()
    
    print(buf.data())
    
    file_path = os.path.dirname(__file__) + os.sep + "test_plotly_vse_adapter.html"
    PlotlifyService.line(y=buf.data()["values"]).to_file(file_path)
    
    
def test_vse_raw_socket():
    sock : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    sock.connect(("192.168.0.10", 3321))
    
    n = 2
    while n > 0:
        bs = sock.recv(2)
        n = len(bs)
        
    sock.close()

    
def test_vse_single_messages():
    
    vse = VSEService(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 10000, thread_type=ThreadType.DAEMON.value)
    
    vse.install()
    
    vse._set_mode(1)
    
    bs = vse._socket.recv(Messages.MSG_ACK.value.n)
    d = struct.unpack(Messages.MSG_ACK.value.sch, bs)
    
    print(d)
    

def test_on_off_vse():
    ot1 = 10
    ot2 = 120
    sr = 10000
        
    ag = Agent()
    
    buf = ListBuffer(capacity=10000000)
    
    ag.add_buffer(buf)
    
    vse = VSEService(host="192.168.0.10",
                     port=3321,
                     sensor = 1,
                     sample_rate = sr,
                     thread_type=ThreadType.ON_OFF_SECONDS.value,
                     mapping_type=MappingType.SUB.value,
                     observing_time=[ot1, ot2]
                     )
    
    vse.add_buffer(buf)
    
    ag.add_service(vse)  
         
    aa = AgentApp(with_api=True, port=8081, agent=ag)
    aa.create()
    aa.run()

    
def test_on_off_vse2csv():
    ot1 = 10
    ot2 = 50
    sr = 10000
    
    ag = Agent()
    
    buf = ListBuffer(capacity=10000000)
    
    ag.add_buffer(buf)
    
    vse = VSEService(host="192.168.0.10",
                     port=3321,
                     sensor = 1,
                     sample_rate = sr,
                     thread_type=ThreadType.ON_OFF_SECONDS.value,
                     mapping_type=MappingType.SUB.value,
                     observing_time=[ot1, ot2]
                     )
    
    vse.add_buffer(buf)
    
    ag.add_service(vse)  
    
    csv = CsvWriteService(folder=os.path.dirname(__file__) + os.sep + "data",
                          file_post_fix="test",
                          max_samples=ot1 * sr * 2,
                          n = 10000,
                          observing_time=1000,
                          thread_type=ThreadType.MILLI_SECOND.value,
                          persistent=False
                          )
    csv.add_buffer(buf) 
    
    ag.add_service(csv) 
    
    aa = AgentApp(with_api=True, port=8081, agent=ag)
    aa.create()
    aa.run() 