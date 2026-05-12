from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.ConfigureElementAction import ConfigureElementAction


def test_000():
    
    ag = Agent()
    
    buf = DictBuffer()
    buf.install(ag)
    
    ag.add_buffer(buf)
    
    buf.push({"key": ""})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install(ag)
    
           
    cea = ConfigureElementAction()
    cea.add_parent(lba)
    cea.install(ag)
    
    cea.execute()
    