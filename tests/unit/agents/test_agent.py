from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer


def test_agent_get_buffer():
    
    ag = Agent()
    
    buf = DictBuffer(id="BUF1")
    
    ag.add_buffer(buf)
        
    assert ag.get_buffer("BUF2") is None, "the buffer was not properly added to bufferstore"
    
def test_agent_get_buffer2():
    
    ag = Agent()
    
    buf = DictBuffer(id="BUF1")
    
    ag.add_buffer(buf)
    
    assert ag.get_buffer("BUF1") is not None, "the buffer was not properly added to bufferstore"