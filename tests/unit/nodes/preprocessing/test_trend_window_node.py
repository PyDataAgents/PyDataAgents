import time

from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.preprocessing.windowing.TrendWindowNode import TrendWindowNode


def test_000():
    
    s = Sine(f = 1.0, a = 1.0, p = 0.0, n = 0.1)
    sb = SignalBuffer(signal = s, capacity=100, sampling_period=100)
    sb.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(sb)
    
    buf = DictBuffer(timestamps_enabled=False, index_enabled=False)
    buf.install()
    twn = TrendWindowNode(max_windows=4, input_keys=["values"], n=10)
    twn.set_buffer(buf)
    twn.add_parent(lba)
    twn.install()
    
    for i in range(1, 6):
        time.sleep(2)
        twn.execute()
        data = twn.get_buffer().data()
        print(data)
        print(len(data))
        assert len(data) == i or i >= twn.max_windows, "number of keys in data must increase with every iteration"
        
    sb.uninstall()