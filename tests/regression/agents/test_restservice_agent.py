from pydag.agents.app.AgentApp import AgentApp
from pydag.services.csv.CsvReadService import CsvReadService
from pydag.services.csv.CsvWriteService import CsvWriteService
from pydag.services.db.SQLService import SQLService
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine


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

    agent.release()

def test_020():
    
    agent = Agent()
    agent.id = "G1"
    
    b1 = ListBuffer()
    agent.add_buffer(b1)
    
    b2 = DictBuffer()
    agent.add_buffer(b2)
    
    s1 = CsvReadService()
    agent.add_service(s1)
    
    s2 = CsvWriteService()
    agent.add_service(s2)    
    
    s3 = SQLService()
    agent.add_service(s3)
        
    app = AgentApp(with_api=True, port=8001)
    app.set_agent(agent)
    app.create()
    app.run()