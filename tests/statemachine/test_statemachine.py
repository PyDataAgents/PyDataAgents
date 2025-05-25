from PyDataGrabber.statemachine.JoinTransition import JoinTransition
from PyDataGrabber.statemachine.Statemachine import Statemachine
from PyDataGrabber.statemachine.actions.SleepAction import SleepAction
from PyDataGrabber.statemachine.actions.StartAction import StartAction
from PyDataGrabber.statemachine.actions.StopAction import StopAction
from PyDataGrabber.statemachine.transitions.TrueTransition import TrueTransition
from PyDataGrabber.tests.statemachine.CountAction import CountAction
from PyDataGrabber.tests.statemachine.CountTransition import CountTransition
from PyDataGrabber.tests.statemachine.PrintAction import PrintAction


def test_000():
    
    n1 = StartAction()
    n2 = CountAction()
    n3 = CountTransition(n2)
    n3.negate = False
    n3.trigger_count = 3
    n4 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n3.add_child(n4)
    
    sm = Statemachine(n1)
    
    sm.start()
    
def test_010():
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
    
    sm = Statemachine(n1)
    
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
    
    sm = Statemachine(n1)
    
    sm.start()
    
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
    
    sm = Statemachine(n1)
    
    sm.start()
    
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
    
    sm = Statemachine(n1)
    
    sm.start()
    
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
    
    sm = Statemachine(n1)
    sm.start()
    
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
    
    sm = Statemachine(n1)
    sm.start()