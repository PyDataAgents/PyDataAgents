from pydag.buffers.DictBuffer import DictBuffer
from pydag.statemachine.actions.buffers.BufferExtractAction import BufferExtractAction


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
    
    
    
    