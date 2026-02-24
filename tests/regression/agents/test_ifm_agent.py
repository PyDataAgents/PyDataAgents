from pydag.adapters.socket.ifmvse.VSEAdapter import VSEAdapter
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.mappings.MappingService import MappingService
from pydag.services.mappings.MappingType import MappingType
from pydag.services.rest.RestService import RestService


def test_000():
    
    ag = Agent()
    
    vse = VSEAdapter(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 100000)
    
    ag.add_adapter(vse)
    
    buf = ListBuffer(id="S1", capacity=300000, duplicate_ids=["S11"])
    
    ag.add_buffer(buf)
    
    m = MappingService()
    m.set_adapter(vse)
    m.add_buffer(buf)
    
    ag.add_service(m)
    
    s = RestService(port=8089)
    
    ag.add_service(s)
    
    ag.release()
    
    