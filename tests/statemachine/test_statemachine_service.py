import os
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.grabbers.GrabberConfig import GrabberConfig
from PyDataGrabber.grabbers.YAMLConfig import YAMLConfig
from PyDataGrabber.statemachine.StatemachineService import StatemachineService
from PyDataGrabber.statemachine.actions.StartAction import StartAction


def test_000():
    
    g = Grabber()
    
    n1 = StartAction()
    
    sms = StatemachineService()
    sms.start_action = n1
    
    sms.add_node(n1)
    
    print(sms.config_options() )
    
    g.add_service(sms)
    
    gc = GrabberConfig(g)
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\grabber_statemachine_config1.yaml")
    
    yc.save(gc)
    
    
def test_010():
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\grabber_statemachine_config1.yaml")
    gc : GrabberConfig = yc.load()
    
    g = gc.create()
    
    print(gc.to_dict())
    
    
    
    
    