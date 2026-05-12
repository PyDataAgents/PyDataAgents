from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.rest.RestService import RestService
from pydag.services.ui.UIService import UIService


def test_000():
    ag = Agent()
    
    buf = DictBuffer(capacity=10)
    ag.add_buffer(buf)
    
    rs = RestService()
    ag.add_service(rs)
    
    uis = UIService(with_mgmt_ui=True, with_buffer_ui=False)
    ag.add_service(uis)
    
    ag.release()
    
def test_010():
    ag = Agent()
    
    s1 = Sine(f=10)
    buf = SignalBuffer(signal=s1, capacity=1000, sampling_period=10)    
    ag.add_buffer(buf)
    
    rs = RestService()
    ag.add_service(rs)
    
    uis = UIService(with_mgmt_ui=True, with_buffer_ui=True)
    ag.add_service(uis)
    
    ag.release()