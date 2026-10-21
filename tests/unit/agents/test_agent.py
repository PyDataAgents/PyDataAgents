import os
import time

import pytest

from pydag.agents.Agent import Agent
from pydag.agents.AgentException import AgentException
from pydag.buffers.Buffer import Buffer
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.utils.PrintAction import PrintAction
from pydag.nodes.utils.SleepAction import SleepAction
from pydag.services.Service import Service
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
    
def test_add_buffer():
    ag = Agent()    
    pa = PrintAction(id="A1", message="Test Message")    
    with pytest.raises(AgentException, match=f"Provided object is not of type {Buffer.__name__}"):
        ag.add_buffer(pa)
        
def test_add_service():
    ag = Agent()    
    pa = PrintAction(id="A1", message="Test Message")    
    with pytest.raises(AgentException, match=f"Provided object is not of type {Service.__name__}"):
        ag.add_service(pa)
        
        
def test_agent_stop_when_idle():
    ag = Agent()
    
    sm = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE)
    sa = SleepAction(sleep_time=3)
    sm.add_node(sa)
    
    ag.add_service(sm)
    
    ag.release(blocking = True, stop_when_idle=True)