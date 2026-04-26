import os

from pydag.adapters.socket.ifmvse.VSEAdapter import VSEAdapter
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.services.ThreadType import ThreadType
from pydag.services.mappings.MappingService import MappingService
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.services.utils.MappingRestartService import MappingRestartService


def test_000():
    ag = Agent()
    
    buf = ListBuffer(capacity=100000)
    ag.add_buffer(buf)
    
    va = VSEAdapter(sensor=1, host="192.168.0.10")
    ag.add_adapter(va)
    
    ms = MappingService()
    ms.set_adapter(va)
    ms.add_buffer(buf)
    ag.add_service(ms)
    
    sas = SimpleActionService(thread_type=ThreadType.SECOND.value, observing_time=1)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    sas.add_node(lba)
    
    plot_path = os.path.dirname(__file__) + "/test_000_plotly.html"
    pa = PlotlifyAction(input_keys=["values"], auto_refresh=1, plot_path=plot_path, n=50000, open_in_browser=False)
    pa.add_parent(lba)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    mrs = MappingRestartService(thread_type=ThreadType.SECOND.value, observing_time=5, restart_attempts=3)
    ag.add_service(mrs)
    
    ag.release()
    