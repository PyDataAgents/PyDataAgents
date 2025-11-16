import os
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
import time


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
                
                
def test_010():
    
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    lba.install()
    
    cda1 = CopyDataAction(n=1000, persistent=True)
    cda1.add_parent(lba)
    cda1.install()
    
    cda2 = CopyDataAction(n=1000, persistent=False)
    cda2.add_parent(lba)
    cda2.install()
    
    plot_path1 = os.path.dirname(__file__) + os.sep + "plotly_1_test010.html"
    data1 = [{"y": "values", "type": "scatter", "mode": "lines"}]
    pa1 = PlotlifyAction(plot_path=plot_path1, data=data1)
    pa1.add_parent(cda1)
    pa1.install()
    
    plot_path2 = os.path.dirname(__file__) + os.sep + "plotly_2_test010.html"
    data2 = [{"y": "values", "type": "scatter", "mode": "lines"}]
    pa2 = PlotlifyAction(plot_path=plot_path2, data=data2)
    pa2.add_parent(cda2)
    pa2.install()
        
    nodes : list[Action] = [lba, cda1, cda2, pa1, pa2]
    
    for node in nodes:
        node.execute()
        if isinstance(node, BufferNode):
            if node.buffer:
                print(node.buffer.data())


def test_011():
    # Test that the data of consumers of two CopyDataAction nodes receives different data between executions.
    # Data of both CopyDataAction nodes is persistent.
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()

    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    # cda1
    cda1 = CopyDataAction(n=10, persistent=True)
    cda1.add_parent(lba)
    cda1.install()
    
    # cda2
    cda2 = CopyDataAction(n=10, persistent=True)
    cda2.add_parent(lba)
    cda2.install()


    i = 0
    while i < 10:
        time.sleep(0.1)
        cda1.execute()
        cda2.execute()
        if hasattr(cda1.buffer, 'data') and hasattr(cda2.buffer, 'data') and cda1.buffer.size() > 0:
            assert cda1.buffer.size() <= 10, f"Size mismatch at iteration {i}" # Buffers have size <= 10
            assert cda2.buffer.size() <= 10, f"Size mismatch at iteration {i}" # Buffers have size <= 10
            assert cda1.buffer.size() == cda2.buffer.size(), f"Size mismatch at iteration {i}" # Buffers have the same size
            assert list(cda1.buffer.data(n=10, persistent=True).values()) == list(cda2.buffer.data(n=10, persistent=True).values()), f"Data mismatch at iteration {i}" # Buffers contain the same data
        i = i + 1



def test_012():
    # TLDR: In each round, each consumer must get different data while two consumers must get the same data from the common source if CopyDataAction(..., persistent=True).
    # 1. Test that a consumer of a CopyDataAction node receives different data between executions. Otherwise this means that always the same data is received and hence useless in downstream applications like e.g. visualization and data processing at the same time.
    # 2. Test that two consumers of two CopyDataAction nodes receives the same data between executions from a common source buffer.
    
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=AgentConfig.INFINITE_CAPACITY)
    sine_buff.install()

    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    print(lba.buffer.size())
    # cda1
    cda1 = CopyDataAction(n=100, persistent=True)
    cda1.add_parent(lba)
    cda1.install()
    
    # cda2
    cda2 = CopyDataAction(n=10, persistent=True)
    cda2.add_parent(lba)
    cda2.install()


    i = 0
    first_round = True
    while i < 100:
        time.sleep(0.3)
        print(lba.buffer.size())
        cda1.execute()
        cda2.execute()
        if hasattr(cda1.buffer, 'data') and hasattr(cda2.buffer, 'data') and cda1.buffer.size() > 0:
            if cda1.buffer.size() >= 10:
                if first_round == True:
                    # First round
                    first_round = False
                    data_first_round_cda1 = list(cda1.buffer.data(n=10, persistent=False).values())
                    data_first_round_cda2 = list(cda2.buffer.data(n=10, persistent=False).values())
                    print(cda1.buffer.size())
                    print(data_first_round_cda1)
                    print(data_first_round_cda2)
                    assert data_first_round_cda1 == data_first_round_cda2, f"Data mismatch at iteration {i}" # Buffers do not contain the same data
                else:
                    # Subsequent rounds
                    try:
                        data_first_round_cda1 = data_later_cd1
                        data_first_round_cda2 = data_later_cd2
                    except:
                        pass
                    data_later_cd1 = list(cda1.buffer.data(n=10, persistent=False).values())
                    data_later_cd2 = list(cda2.buffer.data(n=10, persistent=False).values())
                    print(cda1.buffer.size())
                    print(data_first_round_cda1)
                    print(data_later_cd1)
                    print("##################################")
                    print(cda2.buffer.size())
                    print(data_first_round_cda2)
                    print(data_later_cd2)
                    assert data_first_round_cda1 != data_later_cd1, f"Data match at iteration {i}" # Buffers contain the same data
                    assert data_first_round_cda2 != data_later_cd2, f"Data match at iteration {i}" # Buffers contain the same data
                    assert data_later_cd1 == data_later_cd2, f"Data mismatch at iteration {i}" # Buffers contain the same data
        i = i + 1


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


test_012()