from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine


def test_000():
    ag = Agent(with_api=True, with_ui=True)
    
    buf = DictBuffer(capacity=10)
    ag.add_buffer(buf)
    
    ag.release()
    
def test_010():
    ag = Agent(with_api=True)
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=200)    
    ag.add_buffer(buf)
    
    ag.release()
        
def test_020():
    ag = Agent(with_ui=True)
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=200)    
    ag.add_buffer(buf)
    
    ag.release()
    
def test_030():
    ag = Agent(with_ui=True, with_api=True)
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=10)    
    ag.add_buffer(buf)
    
    ag.release()