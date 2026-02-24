from pydag.adapters.Adapter import Adapter
from pydag.adapters.csv.CsvReadAdapter import CsvReadAdapter
from pydag.agents.AgentElement import AgentElement
from pydag.utils.ClassUtils import ClassUtils


def test_000():
    #ge = GrabberElement()
    
    fields = ClassUtils.get_dataclass_fields(AgentElement)
    print(fields)
    
    
def test_020():
    print(ClassUtils.get_superclasses(CsvReadAdapter))
    
def test_030():
    print(ClassUtils.get_subclasses(Adapter))