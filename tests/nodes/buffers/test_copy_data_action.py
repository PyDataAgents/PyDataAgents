import os
import time
import pytest

from pydag.agents.Agent import Agent
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.services.rest.RestService import RestService
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.mappings.ThreadType import ThreadType
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.agents.AgentConfig import AgentConfig


def test_non_persistent_raises():
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    lba = LinkBufferAction(); lba.set_buffer(db); lba.install()
    cda = CopyDataAction(n=10, persistent=False)
    cda.add_parent(lba); cda.install()
    with pytest.raises(RuntimeError):
        cda.execute()
                
                
def test_forward_initial_snapshot_finite():
    signal = Sine(f=1, a=1, p=0, n=0.02)
    src = SignalBuffer(signal=signal, capacity=50); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=5, persistent=True, forward=True)
    cda.add_parent(lba); cda.install()
    time.sleep(0.15)  # generate some samples
    cda.execute()
    assert cda.buffer.size() <= 5
    # Compare first n samples of source
    head = src.data(n=5, persistent=True)
    copied = cda.buffer.data(n=5, persistent=True)
    assert list(head.values()) == list(copied.values())


def test_forward_shared_and_advancing_finite():
    signal = Sine(f=1, a=1, p=0, n=0.05)
    src = SignalBuffer(signal=signal, capacity=60); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda1 = CopyDataAction(n=10, persistent=True, forward=True); cda1.add_parent(lba); cda1.install()
    cda2 = CopyDataAction(n=10, persistent=True, forward=True); cda2.add_parent(lba); cda2.install()
    prev_data = None
    changes = 0
    for i in range(35):
        time.sleep(0.1)
        cda1.execute(); cda2.execute()
        if cda1.buffer.size() == 0: continue
        d1 = cda1.buffer.data(n=10, persistent=True)
        d2 = cda2.buffer.data(n=10, persistent=True)
        assert list(d1.values()) == list(d2.values()), f"Mismatch between consumers at {i}"
        if prev_data and list(prev_data.values()) != list(d1.values()):
            changes += 1
        prev_data = d1
        assert cda1.buffer.size() <= 10 and cda2.buffer.size() <= 10
    assert changes >= 5, f"Insufficient advancement changes={changes}"

def test_forward_pointer_wrap_finite():
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=5, persistent=True, forward=True); cda.add_parent(lba); cda.install()
    last_pointer = cda.pointer
    advances = 0
    for i in range(50):
        time.sleep(0.08)
        cda.execute()
        if cda.buffer.size() == 0: continue
        assert cda.pointer >= last_pointer, "Pointer regressed"
        if cda.pointer > last_pointer:
            advances += 1
        last_pointer = cda.pointer
        assert cda.buffer.size() <= 5
    assert advances >= 10, f"Too few pointer advances: {advances}"


def test_forward_infinite_capacity_advancing():
    signal = Sine(f=1, a=1, p=0, n=0.05)
    src = SignalBuffer(signal=signal, capacity=AgentConfig.INFINITE_CAPACITY); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda1 = CopyDataAction(n=15, persistent=True, forward=True); cda1.add_parent(lba); cda1.install()
    cda2 = CopyDataAction(n=15, persistent=True, forward=True); cda2.add_parent(lba); cda2.install()
    last_pointer = cda1.pointer
    changes = 0
    prev_vals = None
    for i in range(30):
        time.sleep(0.1)
        cda1.execute(); cda2.execute()
        if cda1.buffer.size() == 0: continue
        d1 = cda1.buffer.data(n=15, persistent=True)
        d2 = cda2.buffer.data(n=15, persistent=True)
        assert list(d1.values()) == list(d2.values())
        assert cda1.pointer >= last_pointer
        if cda1.pointer > last_pointer:
            changes += 1
        last_pointer = cda1.pointer
        if prev_vals and list(prev_vals.values()) != list(d1.values()):
            pass
        prev_vals = d1
        assert cda1.buffer.size() <= 15 and cda2.buffer.size() <= 15
    assert changes >= 10, f"Advancement insufficient changes={changes}"


def test_000():
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    lba.install()
    
    cba1 = CopyDataAction(n=1000, persistent=True)
    cba1.add_parent(lba)
    cba1.install()
    
    cba2 = CopyDataAction(n=1000, persistent=False)
    cba2.add_parent(cba1)
    cba2.install()
    
    nodes : list[Action] = [lba, cba1, cba2]
    
    for i in range(0, 5):
        print(i)
        for node in nodes:
            node.execute()
            if isinstance(node, BufferNode):
                print(node.buffer.data())

def test_020():
    """ generates an agent for grafana testing of two plots showing the same time series data as data stream from dataset buffer
    """
    agent = Agent()
    
    db = DatasetBuffer(id="DB", dataset_name="ArrowHead")
    
    agent.add_buffer(db)
    
    rs = RestService(port=10011)
    
    agent.add_service(rs)
    
    sas = SimpleActionService(thread_type=ThreadType.MILLI_SECOND, sampling_period=5000)
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    sas.add_node(lba)
    
    cda1 = CopyDataAction(buffer_id="B1", n=1000, persistent=True)
    cda1.add_parent(lba)
    sas.add_node(cda1)
    
    cda2 = CopyDataAction(buffer_id="B2", n=1000, persistent=False)
    cda2.add_parent(lba)
    sas.add_node(cda2)
    
    agent.add_service(sas)   
    
    agent.start_blocking()