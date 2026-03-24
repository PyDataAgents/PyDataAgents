import time

from pydag.agents.Agent import Agent
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.ThreadType import ThreadType
from pydag.services.utils.AgentPersistService import AgentPersistService


def test_000():
    
    ag = Agent()
    
    s = Sine()
    sb = SignalBuffer(signal=s, sampling_period=100, load_on_install=True, capacity=20)
    
    ag.add_buffer(sb)
    
    ps = AgentPersistService(thread_type=ThreadType.SECOND.value, observing_time=3)
    ag.add_service(ps)
    
    ag.release(blocking=False)
    
    time.sleep(10)
    
    ag.terminate()