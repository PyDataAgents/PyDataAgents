
from pydag.adapters.csv.CsvReadAdapter import CsvReadAdapter
from pydag.adapters.csv.CsvWriteAdapter import CsvWriteAdapter
from pydag.adapters.db.SQLAdapter import SQLAdapter
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
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

    agent.release()

def test_020():
    
    agent = Agent()
    agent.id = "G1"
    
    b1 = ListBuffer()
    agent.add_buffer(b1)
    
    b2 = DictBuffer()
    agent.add_buffer(b2)
    
    adapter1 = CsvReadAdapter()
    agent.add_adapter(adapter1)
    
    adapter2 = CsvWriteAdapter()
    agent.add_adapter(adapter2)    
    
    adapter3 = SQLAdapter()
    agent.add_adapter(adapter3)
    
    service = RestService(id = "S1", port=8001)
    agent.add_service(service)
    
    agent.release()