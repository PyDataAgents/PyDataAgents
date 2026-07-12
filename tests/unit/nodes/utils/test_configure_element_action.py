from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.ConfigureElementAction import ConfigureElementAction


def test_000():
    
    ag = Agent()
    
    buf = DictBuffer(id="B1", capacity=1)
    buf.install(ag)
    
    ag.add_buffer(buf)
    
    new_capacity = 2
    buf.push({"capacity": new_capacity})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install(ag)
    
           
    cea = ConfigureElementAction(option="capacity", element_id="B1")
    cea.add_parent(lba)
    cea.install(ag)
    
    cea.execute()
    
    assert buf.capacity == new_capacity
    