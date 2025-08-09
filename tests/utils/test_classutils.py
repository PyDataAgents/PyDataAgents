from pydag.agents.AgentElement import AgentElement
from pydag.utils.ClassUtils import ClassUtils


def test_000():
    #ge = GrabberElement()
    
    fields = ClassUtils.get_dataclass_fields(AgentElement)
    print(fields)
    
def test_010():
    ge = AgentElement()
    
    ClassUtils.set_property(ge, "id", "test_id")
    
    print(ge)