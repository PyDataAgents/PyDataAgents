import time
from pydag.buffers.DataType import DataType
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.agents.Agent import Agent
from pydag.services.rest.RestService import RestService

    
def test_010():
    agent = Agent(id = "G1")
    
    s = Sine()
    b = SignalBuffer(signal = s, capacity = 100, id = "S1", sampling_period = 100, unit = "V", data_type = DataType.FLOAT.value)
    b.install()

    agent.add_buffer(b)

    service = RestService(id = "S1")
    service.install(agent)
    
    service.start()
    
    time.sleep(5)
    
    service.stop()
