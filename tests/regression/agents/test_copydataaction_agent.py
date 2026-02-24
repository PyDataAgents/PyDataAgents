
from pydag.agents.Agent import Agent
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.services.ThreadType import ThreadType
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.rest.RestService import RestService
from pydag.services.statemachine.SimpleActionService import SimpleActionService


def test_020():
    """ generates an agent for grafana testing of two plots showing the same time series data as data stream from dataset buffer
    """
    agent = Agent()
    
    db = DatasetBuffer(id="DB", dataset_name="ArrowHead")
    
    agent.add_buffer(db)
    
    rs = RestService(port=10011)
    
    agent.add_service(rs)
    
    sas = SimpleActionService(thread_type=ThreadType.MILLI_SECOND, observing_time=5000)
    
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
    
    agent.release()