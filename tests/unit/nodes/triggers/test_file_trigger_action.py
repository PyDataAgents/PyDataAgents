import os
from pydag.agents.Agent import Agent
from pydag.nodes.triggers.FileTriggerAction import FileTriggerAction
from pydag.nodes.utils.PrintBufferAction import PrintBufferAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.utils.FileUtils import FileUtils


def test_000():
    folder = FileUtils.user_home() + os.sep + "Downloads"   
    
    ag = Agent()
        
    sas = SimpleActionService(thread_type=ThreadType.TRIGGERED.value)
    
    fta = FileTriggerAction(folder=folder, create_events=False, modified_events=True)
    fta.set_service(sas)
    sas.add_node(fta)

    
    pa = PrintBufferAction(persistent=False)
    pa.add_parent(fta)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    ag.release()
    
    
def test_001():
    folder = FileUtils.user_home() + os.sep + "Downloads"   
    
    ag = Agent()
        
    sas = SimpleActionService(thread_type=ThreadType.TRIGGERED.value)
    
    fta = FileTriggerAction(folder=folder, create_events=True, recursive=True)
    fta.set_service(sas)
    sas.add_node(fta)

    
    pa = PrintBufferAction(persistent=False)
    pa.add_parent(fta)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    ag.release()
    
    
def test_002():
    folder = FileUtils.user_home() + os.sep + "Downloads"   
    
    ag = Agent()
        
    sas = SimpleActionService(thread_type=ThreadType.TRIGGERED.value)
    
    fta = FileTriggerAction(folder=folder, create_events=False, modified_events=True)
    fta.set_service(sas)
    sas.add_node(fta)

    
    pa = PrintBufferAction(persistent=False)
    pa.add_parent(fta)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    ag.release()
    

def test_003():
    folder = FileUtils.user_home() + os.sep + "Downloads"   
    
    ag = Agent()
        
    sas = SimpleActionService(thread_type=ThreadType.TRIGGERED.value)
    
    fta = FileTriggerAction(folder=folder, create_events=False, delete_events=True, recursive=True)
    fta.set_service(sas)
    sas.add_node(fta)

    
    pa = PrintBufferAction(persistent=False)
    pa.add_parent(fta)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    ag.release()