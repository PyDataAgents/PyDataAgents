from pydag.agents.AgentElement import AgentElement
from pydag.services.Service import Service
from pydag.services.csv.CsvReadService import CsvReadService
from pydag.services.datamodel.DataModel import DataModel
from pydag.utils.ClassUtils import ClassUtils


def test_000():
    #ge = GrabberElement()
    
    fields = ClassUtils.get_dataclass_fields(AgentElement)
    print(fields)
    
    
def test_020():
    print(ClassUtils.get_superclasses(CsvReadService))
    
def test_030():
    print(ClassUtils.get_subclasses(Service))
    
    
def test_040():
    res = ClassUtils.find_subclasses(DataModel, "tests\\unit\\services\\datamodel")
    print(res)
    
def test_041():
    res = ClassUtils.find_subclasses(Service, "pydag\\services")
    print(res)