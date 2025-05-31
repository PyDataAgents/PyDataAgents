import time
from PyDataGrabber.pydatagrabber.buffers.SignalBuffer import SignalBuffer
from PyDataGrabber.pydatagrabber.buffers.signals.Sine import Sine


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
    sb = SignalBuffer()
    sb.signal = s
    sb.capacity=10
    sb.sampling_period=100
    i = 0
    while i < 10:
        time.sleep(0.1)
        print(sb.data(3, False))
        i = i + 1
    
    