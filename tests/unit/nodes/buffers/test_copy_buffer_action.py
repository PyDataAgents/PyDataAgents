import time
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.buffers.CopyBufferAction import CopyBufferAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.Action import Action

def test_000():
    
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    lba.install()
    
    cba = CopyBufferAction()
    cba.add_parent(lba)
    cba.install()
    
    nodes : list[Action] = [lba, cba]
    
    for node in nodes:
        node.execute()
        if isinstance(node, BufferNode):
            if node.get_buffer():
                print(node.get_buffer().data())
                
def test_010():
    
    s = Sine()
    sb = SignalBuffer(signal=s, sampling_period=100, capacity=100)
    sb.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(sb)
    lba.install()
    
    cba = CopyBufferAction()
    cba.add_parent(lba)
    cba.install()
    
    nodes : list[Action] = [lba, cba]
    
    for i in range(0, 5):
        print(i)
        time.sleep(0.5)
        for node in nodes:
            node.execute()
            if isinstance(node, BufferNode):
                if node._buffer:
                    print(node._buffer.data())