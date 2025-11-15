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