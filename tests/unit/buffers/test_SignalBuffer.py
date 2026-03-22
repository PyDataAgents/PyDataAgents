import time
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine


def test_000():
    s = Sine()
    s.f = 1.0
    s.a = 1.0
    s.p = 0.0
    s.n = 0.1
    t, v = s.value()
    print(f"Sine value at t={t} ms: {v}")
    t, v = s.value()
    print(f"Sine value at t={t} ms: {v}")
    
def test_010():
    s = Sine()
    s.f = 1.0
    s.a = 1.0
    s.p = 0.0
    s.n = 0.1
    sb = SignalBuffer(signal = s, capacity=10, sampling_period=100)
    sb.install()
    i = 0
    while i < 10:
        time.sleep(0.1)
        print(sb.data(1, False))
        i = i + 1
        
    sb.uninstall()
    
    