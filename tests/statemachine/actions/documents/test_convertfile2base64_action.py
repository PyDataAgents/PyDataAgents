import os

from pydag.agents.Agent import Agent
from pydag.mappings.ThreadType import ThreadType
from pydag.services.rest.RestService import RestService
from pydag.statemachine.StatemachineService import StatemachineService
from pydag.statemachine.actions.StopAction import StopAction
from pydag.statemachine.actions.documents.ConvertFile2Base64Action import ConvertFile2Base64Action


def test_000():
    
    file_paths = [os.path.dirname(__file__) + os.sep + "This is a Test PDF.pdf"]
    
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)    
    cf2b64a.install()    
    cf2b64a.execute()    
    print(cf2b64a.buffer.data())
    
def test_010():
    file_paths = [os.path.dirname(__file__) + os.sep + "test-image.png"]
    
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)
    
    cf2b64a.install()
    
    cf2b64a.execute()
    
    print(cf2b64a.buffer.data())
    
def test_020():
    
    ag = Agent()
    
    rs = RestService(port=8001)
    ag.add_service(rs)
    
    file_paths = [os.path.dirname(__file__) + os.sep + "This is a Test PDF.pdf", os.path.dirname(__file__) + os.sep + "test-image.png"]
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)
    
    sa = StopAction()
    sa.add_parent(cf2b64a)
    
    sms = StatemachineService(thread_type=ThreadType.ONLY_ONCE.value)
    sms.add_node(cf2b64a)
    sms.add_node(sa)
    sms.start_action = cf2b64a
    
    ag.add_service(sms)
    
    ag.start_blocking()