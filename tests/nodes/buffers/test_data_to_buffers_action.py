import time
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.nodes.buffers.DataToBuffersAction import DataToBuffersAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_000():
    
    s = Sine()
    sb = SignalBuffer(signal=s, capacity=20, sampling_period=100)
    sb.install()
    
    dtba = DataToBuffersAction(buffer_ids=["B1", "B2"], n=5, persistent=False)
    dtba.set_buffer(sb)
    dtba.install()
    
    print(dtba.buffers)

    sb.uninstall()
    
def test_010():
    
    s = Sine()
    sb = SignalBuffer(signal=s, capacity=20, sampling_period=100)
    sb.install()
    
    time.sleep(1)
    
    dtba = DataToBuffersAction(buffer_ids=["B1", "B2"], n=5, persistent=False)
    dtba.set_buffer(sb)
    dtba.install()
    
    dtba.execute()
    
    sb.uninstall()
    
    if dtba.buffers["B1"].data() == dtba.buffers["B2"].data():
        assert True
    else:
        assert False    
        
def test_011():
    
    s = Sine()
    sb = SignalBuffer(signal=s, capacity=20, sampling_period=100)
    sb.install()
    
    time.sleep(1)
    
    lba = LinkBufferAction()
    lba.set_buffer(sb)
    lba.install()
    
    dtba = DataToBuffersAction(buffer_ids=["B1", "B2"], n=5, persistent=False)
    dtba.add_parent(lba)
    dtba.install()
    
    dtba.execute()
    
    sb.uninstall()
    
    if dtba.buffers["B1"].data() == dtba.buffers["B2"].data():
        assert True
    else:
        assert False 

    