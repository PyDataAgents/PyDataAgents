import time
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sawtooth import Sawtooth


def test_000():
    st = Sawtooth()
    
    sb = SignalBuffer()
    sb.signal = st
    sb.capacity = 1
    sb.sampling_period = 100
    
    sb.install()
    
    i = 0
    while i < 200:
        time.sleep(0.025)
        print(sb.data())
        i = i + 1
        
    sb.uninstall()    