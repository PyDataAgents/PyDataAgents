
import os

from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService


def test_iolink_service_vvb301_app():
    
    ag = Agent()
    
    buf = DictBuffer(capacity=500)
    ag.add_buffer(buf)
        
    host = "http://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"
    scaling = {"Temperature": 0.1, "Crest": 0.1, "Fatigue (v-RMS)": 0.0001, "Friction (a-RMS)": 0.01}    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value, observing_time=100, scaling=scaling)
    ios.add_buffer(buf)
    
    ag.add_service(ios)
    
    aa = AgentApp(agent=ag, with_ui=True)
    aa.create()
    aa.run()
    