from pydag.adapters.socket.ifmvse.VSEAdapter import VSEAdapter
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.mappings.MappingService import MappingService


def test_000():
    ag = Agent()
    
    buf = ListBuffer(capacity=100000)
    ag.add_buffer(buf)
    
    va = VSEAdapter(sensor=1, host="192.168.0.10")
    ag.add_adapter(va)
    
    ms = MappingService()
    ms.set_adapter(va)
    ms.add_buffer(buf)
    ag.add_service(ms)
    
    ag.release()
    