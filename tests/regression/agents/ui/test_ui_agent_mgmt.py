from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine


def test_000():
    ag = Agent()
    
    buf = DictBuffer(capacity=10)
    ag.add_buffer(buf)
    
    app = AgentApp(port=8081, with_api=True, with_ui=True, dark_mode=False)
    app.set_agent(ag)
    app.create()
    app.run()
    
def test_010():
    ag = Agent()
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=200)    
    ag.add_buffer(buf)
    
    app = AgentApp(port=8081, with_api=True, dark_mode=False)
    app.set_agent(ag)
    app.create()
    app.run()
        
def test_020():
    ag = Agent()
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=200)    
    ag.add_buffer(buf)
    
    app = AgentApp(port=8081, with_ui=True, with_api=False, dark_mode=False)
    app.set_agent(ag)
    app.create()
    app.run()
    
def test_030():
    ag = Agent(with_ui=True, with_api=True)
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=10)    
    ag.add_buffer(buf)
    
    ag.release()