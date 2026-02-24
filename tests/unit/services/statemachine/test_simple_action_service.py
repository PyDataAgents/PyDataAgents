from pydag.nodes.utils.SleepAction import SleepAction
from pydag.services.Service import Service
from pydag.services.statemachine.SimpleActionService import SimpleActionService


def test_install():
    sas = SimpleActionService()
    
    sa = SleepAction()
    sas.add_node(sa)
    
    sas.install()
    
def test_install_from_dict():
    d : dict[str, Service] = {}
    sas = SimpleActionService()
    d[sas.id] = sas
    
    sa = SleepAction()
    sas.add_node(sa)
    
    for service in d.values():
        service.install()