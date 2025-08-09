import time
from pydag.buffers.DataType import DataType
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.agents.Agent import Agent
from pydag.services.rest.RestService import RestService

def test_000():
    agent = Agent()
    agent.id = "G1"
    
    s = Sine()
    b = SignalBuffer()
    b.signal = s
    b.capacity = 100
    b.id = "S1"
    b.sampling_period = 100 # ms
    b.unit = "V"
    b.data_type = DataType.FLOAT.value

    agent.add_buffer(b)

    service = RestService()
    service.id = "S1"
    
    agent.add_service(service)

    agent.start_blocking()
    
def test_010():
    agent = Agent()
    agent.id = "G1"
    
    s = Sine()
    b = SignalBuffer()
    b.signal = s
    b.capacity = 100
    b.id = "S1"
    b.sampling_period = 100 # ms
    b.unit = "V"
    b.data_type = DataType.FLOAT.value

    agent.add_buffer(b)

    service = RestService()
    service.id = "S1"
    service.install(agent)
    
    service.start()
    
    time.sleep(5)
    
    service.stop()
