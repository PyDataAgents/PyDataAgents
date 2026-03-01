import os
import time
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
    
    ag.release(blocking=False)
    
    time.sleep(1.0)
    
    # In a real test, we would want to programmatically create/modify files in the folder to trigger the action and verify the output.
    with open(folder + os.sep + "test_file_trigger.txt", "w", encoding="utf-8") as f:
        f.write("This is a test file to trigger the FileTriggerAction.")
    
    time.sleep(1.0)
        
    ag.terminate()
    
    
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
    
    ag.release(blocking=False)
    
    time.sleep(1.0)
    
    # In a real test, we would want to programmatically create/modify files in the folder to trigger the action and verify the output.
    with open(folder + os.sep + "test_file_trigger.txt", "w", encoding="utf-8") as f:
        f.write("This is a test file to trigger the FileTriggerAction.")
        
    FileUtils.create_dir(folder + os.sep + "test_subfolder")
    # In a real test, we would want to programmatically create/modify files in the folder to trigger the action and verify the output.
    with open(folder + os.sep + "test_subfolder" + os.sep + "test_file_trigger2.txt", "w", encoding="utf-8") as f:
        f.write("This is a test file to trigger the FileTriggerAction.")
    
    time.sleep(1.0)
        
    ag.terminate()
    
    
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
    
    ag.release(blocking=False)
    
    time.sleep(1.0)
    
    # In a real test, we would want to programmatically create/modify files in the folder to trigger the action and verify the output.
    with open(folder + os.sep + "test_file_trigger.txt", "w", encoding="utf-8") as f:
        f.write("This is a modified test file to trigger the FileTriggerAction.")
    
    time.sleep(1.0)
        
    ag.terminate()
    

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
    
    ag.release(blocking=False)
    
    time.sleep(1.0)
    
    FileUtils.delete_file(folder + os.sep + "test_file_trigger.txt")
    
    time.sleep(1.0)
        
    ag.terminate()
