from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.ConfigureElementAction import ConfigureElementAction


def test_000():
    buf = DictBuffer()
    buf.install()
    
    buf.push({"key": ""})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
           
    cea = ConfigureElementAction()
    cea.add_parent(lba)
    cea.install()
    
    cea.execute()
    