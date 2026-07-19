import os
import time

from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.utils.PrintAction import PrintAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine


def test_agent_get_buffer():
    
    ag = Agent()
    
    buf = DictBuffer(id="BUF1")
    
    ag.add_buffer(buf)
        
    assert ag.get_buffer("BUF2") is None, "the buffer was not properly added to bufferstore"
    
def test_agent_get_buffer2():
    
    ag = Agent()
    
    buf = DictBuffer(id="BUF1")
    
    ag.add_buffer(buf)
    
    assert ag.get_buffer("BUF1") is not None, "the buffer was not properly added to bufferstore"
    
def test_load_agent():
    ag = Agent.load_from(os.path.dirname(__file__) + os.sep + "config.yaml")
    ag.release(blocking=False)
    time.sleep(5)    
    ag.terminate()
    
def test_edit_agent_element():
    ag = Agent()
    
    buf = DictBuffer(id="BUF1")
    
    ag.add_buffer(buf)
    
    ag.edit_element(buf.id, {"id": "BUF11"})
    
    assert buf.id == "BUF11", "wrong buffer id"
    
    
def test_edit_agent_element2():
    ag = Agent()
    
    sas = SimpleStatemachine(
        thread_type=ThreadType.SECOND.value,
        observing_time=1.0
    )
    
    pa = PrintAction(id="A1", message="Test Message")
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    ag.release(blocking=False)
    
    time.sleep(3)
    
    ag.edit_element("A1", {"id": "A11"})
    
    time.sleep(3)
    
    ag.terminate()
    
    assert pa.id == "A11", "wrong id was specififed"
    
    