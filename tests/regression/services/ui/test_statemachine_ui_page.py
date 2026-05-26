from pydag.agents.Agent import Agent
from pydag.nodes.triggers.ObserverTriggerAction import ObserverTriggerAction
from pydag.nodes.utils.PrintAction import PrintAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.services.ui.UIStatemachinePage import UIStatemachinePage
from pydag.services.ui.UIService import UIService


def test_000():
    ag = Agent()
    
    sas = SimpleActionService(thread_type=ThreadType.TRIGGERED.value, description="Test StatemachineService, that outlines how the UI can be used to trigger statemachines. This is a example only, to showcase the UI, and is not meant to be a real service.")
    
    ota = ObserverTriggerAction()
    ota.set_service(sas)
    sas.add_node(ota)
    
    pa = PrintAction(message="Statemachine Triggered!")
    ota.add_parent(pa)
    sas.add_node(pa)
    
    ag.add_service(sas)
    
    uis = UIService(with_mgmt_ui=True, with_buffer_ui=True)
    uis.add_page(UIStatemachinePage(uis))
    ag.add_service(uis)
    
    ag.release()