import os
from pydag.agents.Agent import Agent
from pydag.services.ThreadType import ThreadType
from pydag.nodes.documents.ConvertFile2Base64Action import ConvertFile2Base64Action
from pydag.nodes.utils.StopAction import StopAction
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.documents.ListFilesAction import ListFilesAction


def test_020():
    
    ag = Agent(with_api=True, port=8001)
        
    file_paths = [os.path.dirname(__file__) + os.sep + "This is a Test PDF.pdf", os.path.dirname(__file__) + os.sep + "test-image.png"]
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)
    
    sa = StopAction()
    sa.add_parent(cf2b64a)
    
    sms = SimpleActionService(thread_type=ThreadType.ONLY_ONCE.value)
    sms.add_node(cf2b64a)
    sms.add_node(sa)
    
    ag.add_service(sms)
    
    ag.release()
    
def test_000():
    ag = Agent(with_api=True, port=8001)
    
    buf = ListBuffer(id="B1")
    ag.add_buffer(buf)    
        
    folder = os.path.dirname(__file__) + os.sep + "data"
        
    lfa = ListFilesAction(folder=folder)
    lfa.set_buffer(buf)
    
    buf2 = ListBuffer(id="B2")
    ag.add_buffer(buf2)
    
    cba = ConvertFile2Base64Action(input_keys=["values"])
    cba.add_parent(lfa)
    cba.set_buffer(buf2)
    
    sas = SimpleActionService(id="S1", thread_type=ThreadType.ONLY_ONCE)
    sas.add_node(lfa)
    sas.add_node(cba)
    ag.add_service(sas)
        
    ag.release()
    