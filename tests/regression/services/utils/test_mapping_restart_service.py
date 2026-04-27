import os

from pydag.services.socket.ifmvse.VSEService import VSEService
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.services.utils.MappingRestartService import MappingRestartService


def test_000():
    ag = Agent()
    
    buf = ListBuffer(id="B1", capacity=100000)
    ag.add_buffer(buf)
    
    va = VSEService(id="A1", sensor=1, host="192.168.0.10")
    va.add_buffer(buf)    
    ag.add_service(va)
    
    sas = SimpleActionService(id="S1", thread_type=ThreadType.SECOND.value, observing_time=1)
    
    lba = LinkBufferAction(id="L1")
    lba.set_buffer(buf)
    sas.add_node(lba)
    
    plot_path = os.path.dirname(__file__) + "/test_000_plotly.html"
    pa = PlotlifyAction(id="P1", input_keys=["values"], auto_refresh=1, plot_path=plot_path, n=50000, open_in_browser=False)
    pa.add_parent(lba)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    mrs = MappingRestartService(id="R1", thread_type=ThreadType.SECOND.value, observing_time=5, restart_attempts=3)
    ag.add_service(mrs)
    
    ag.release()
    