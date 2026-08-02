import os
import time
from pydag.agents.Agent import Agent
from pydag.agents.AgentKeywords import AgentKeywords
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.nodes.utils.JoinTransition import JoinTransition
from pydag.services.statemachine.SFCService import SFCService
from pydag.services.statemachine.StatemachineException import StatemachineException
from pydag.nodes.utils.SleepAction import SleepAction
from pydag.nodes.utils.StartAction import StartAction
from pydag.nodes.utils.StopAction import StopAction
from pydag.nodes.utils.TrueTransition import TrueTransition
from pydag.nodes.utils.CountAction import CountAction
from pydag.nodes.utils.CountTransition import CountTransition
from pydag.nodes.utils.PrintAction import PrintAction
<<<<<<< HEAD
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine
=======
>>>>>>> develop
from pydag.services.ThreadType import ThreadType


def test_000():
    
    g = Agent()
    
    n1 = StartAction()
    
    sms = SFCService()
        
    sms.add_node(n1)
    
    print(sms.config_options() )
    
    g.add_service(sms)
    
    gc = AgentKeywords(g)
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_statemachine_config1.yaml")
    
    yc.save(gc)
    
    
def test_001():
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_statemachine_config1.yaml")
    gc : AgentKeywords = yc.load()
    
    g = gc.create()
    
    print(gc.to_dict())
    
    

def test_010():
    
    n1 = StartAction()
    n2 = CountAction()
    n3 = CountTransition(n2)
    n3.negate = False
    n3.trigger_count = 3
    n4 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n3.add_child(n4)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.install()
    sm.start()
    
def test_011():
    
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "I'm going to sleep"
    n3 = SleepAction()
    n3.sleep_time = 2
    n4 = PrintAction()
    n4.message = "I'm awake now"
    n5 = CountAction()
    n6 = CountTransition(n5)
    n6.negate = False
    n6.trigger_count = 5
    n7 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n3.add_child(n4)
    n4.add_child(n5)
    n5.add_child(n6)
    n6.add_child(n7)
    
    sm = SFCService()
    sm.add_node(n1) 
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.add_node(n7)
    sm.install()
    sm.start()
    
    
def test_020():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = StopAction()
    n6 = PrintAction()
    n6.message = "3"
    n7 = TrueTransition()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n6)
    n6.add_child(n7)
    n7.add_child(n2)
    
    sm = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.add_node(n7)
    sm.install()
    
    sm.start()    
    time.sleep(5)    
    sm.stop()
    
    
def test_021():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = StopAction()
    n6 = PrintAction()
    n6.message = "3"
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n6)
    n6.add_child(n2)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    try:    
        sm.install()
        sm.start()
    except StatemachineException as se:
        print("RecursionError caught as expected: ", se)
    
def test_030():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = PrintAction()
    n5.message = "3"
    n6 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n5)
    n5.add_child(n6)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.install()
    try:
        sm.start()
    except StatemachineException as se:
        print("StatemachineException caught as expected: ", se) 
    
def test_040():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = PrintAction()
    n5.message = "3"
    n6 = PrintAction()
    n6.message = "4"
    n7 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n6)
    n5.add_child(n6)
    n6.add_child(n7)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.add_node(n7)
    sm.install()
    
    try:
        sm.start()
    except StatemachineException as se:
        print("StatemachineException caught as expected: ", se)
    
def test_050():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = PrintAction()
    n5.message = "3"
    n6 = JoinTransition()
    n7 = PrintAction()
    n7.message = "4"
    n8 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n6)
    n5.add_child(n6)
    n6.add_child(n7)
    n7.add_child(n8)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.add_node(n7)
    sm.add_node(n8)
    sm.install()
    sm.start()

def test_060():
    """Test that SimpleStatemachine executes each Action exactly once with ONLY_ONCE thread type."""
    # Arrange
    a1 = StartAction()
    a2 = CountAction()
    a3 = StopAction()
    a1.add_child(a2)
    a2.add_child(a3)

    service = SimpleStatemachine()
    service.add_node(a1)
    service.add_node(a2)
    service.add_node(a3)
    # Force ONLY_ONCE execution semantics
    service.thread_type = ThreadType.ONLY_ONCE.value
    service.install()
    
    # Act
    service.start()
    # Wait for thread to finish (ONLY_ONCE runs observer once and returns)
    service._thread.join(timeout=2)

    # Assert
    # StartAction inherits Action but doesn't increment count; CountAction increments once
    assert a2.count == 1, f"Expected CountAction to execute once, executed {a2.count} times"
    assert service._thread.is_alive() is False
    
