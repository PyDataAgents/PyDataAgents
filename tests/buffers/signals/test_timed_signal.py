import time
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.TimedSignal import TimedSignal


def test_000():
    ts = TimedSignal()
    ts.times = [1, 3, 5, 10, 15, 18]
    ts.values = [10, 20, 30, 40, 50, 60]
    
    sb = SignalBuffer()
    sb.signal = ts
    sb.capacity=1
    sb.sampling_period=100
    
    sb.install()
    
    i = 0
    while i < 200:
        time.sleep(0.1)
        print(sb.data())
        i = i + 1
        
    sb.deinstall()    