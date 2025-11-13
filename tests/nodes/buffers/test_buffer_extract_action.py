from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.BufferExtractAction import BufferExtractAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.buffers.ParentBufferExtractAction import ParentBufferExtractAction


def test_000():
    
    buf = DictBuffer(id="B1", capacity=5)
    buf.initial_values = {
        "A": [1,2,3,4,5],
        "B": [6,7,8,9,10]
    }
    buf.install()
    
    bea = BufferExtractAction()
    bea.extract_buffer = buf
    bea.extract_keys = ["B"]
    bea.install()
    
    bea.execute()
    
    print(bea.buffer.data())
    
    
def test_001(): 
    
    buf = DictBuffer(id="B1", capacity=5)
    buf.initial_values = {
        "A": [1,2,3,4,5],
        "B": [6,7,8,9,10]
    }
    buf.install()
    
    lba = LinkBufferAction()
    lba.buffer = buf
    lba.install()
    
    bea = ParentBufferExtractAction()
    bea.extract_keys = ["B"]
    bea.add_parent(lba)
    bea.install()
    
    bea.execute()
    
    print(bea.buffer.data())
    
    
    