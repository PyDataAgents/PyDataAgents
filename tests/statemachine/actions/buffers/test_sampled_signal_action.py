from pydag.buffers.signals.SampledSine import SampledSine
from pydag.statemachine.actions.buffers.SampledSignalAction import SampledSignalAction


def test_000():    
    ss = SampledSine(sample_rate=10)    
    ssa = SampledSignalAction(signal=ss, n=1000)
    ssa.install()    
    ssa.execute()    
    print(ssa.buffer.data())    