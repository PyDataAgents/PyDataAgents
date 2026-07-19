from pydag.nodes.utils.SleepAction import SleepAction
from pydag.services.Service import Service
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine


def test_install():
    sas = SimpleStatemachine()
    
    sa = SleepAction()
    sas.add_node(sa)
    
    sas.install()
    
def test_install_from_dict():
    d : dict[str, Service] = {}
    sas = SimpleStatemachine()
    d[sas.id] = sas
    
    sa = SleepAction()
    sas.add_node(sa)
    
    for service in d.values():
        service.install()