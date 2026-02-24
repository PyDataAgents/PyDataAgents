import time
from pydag.buffers.SampledBuffer import SampledBuffer
from pydag.buffers.signals.SampledSine import SampledSine


def test_000():
    
    ss = SampledSine()    
    ss.f = 100
    ss.sample_rate = 1000
    ss.install()
    
    sb = SampledBuffer(capacity=400)
    sb.signal = ss
    sb.sampling_period = 100
    sb.n = 1
    sb.install()
    
    w = 0
    while w < 20:
        time.sleep(0.1)
        print(sb.data(persistent=True))       
        w = w + 1