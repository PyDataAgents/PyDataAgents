from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.signals.TimedSignal import TimedSignal


def test_000():
    
    ag = Agent()
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=10)    
    ag.add_buffer(buf)
    
    s2 = Sine(f=1)
    buf2 = SignalBuffer(signal=s2, capacity=100, sampling_period=10)    
    ag.add_buffer(buf2)
    
    ts = TimedSignal()
    ts.times = [1, 3, 5, 10, 15, 18]
    ts.values = [10, 20, 30, 40, 50, 60]
    
    sb = SignalBuffer()
    sb.signal = ts
    sb.capacity=1000
    sb.sampling_period=100
    
    ag.add_buffer(sb)
        
    app = AgentApp(port=10001, with_ui=True, with_api=True, dark_mode=False)
    app.set_agent(ag)
    app.create()
    app.run()
    
def test_010():
    ag = Agent()
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=10)    
    ag.add_buffer(buf)
    
    s2 = Sine(f=1)
    buf2 = SignalBuffer(signal=s2, capacity=100, sampling_period=10)    
    ag.add_buffer(buf2)
    
    ts = TimedSignal()
    ts.times = [1, 3, 5, 10, 15, 18]
    ts.values = [10, 20, 30, 40, 50, 60]
    
    sb = SignalBuffer()
    sb.signal = ts
    sb.capacity=1000
    sb.sampling_period=100
    
    ag.add_buffer(sb)
    
    app = AgentApp(port=10001, with_ui=True, with_api=True, dark_mode=False)
    app.set_agent(ag)
    app.create()
    app.run()
    