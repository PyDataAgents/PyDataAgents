from pydatagrabber.grabbers.GrabberElement import GrabberElement
from pydatagrabber.utils.ClassUtils import ClassUtils


def test_000():
    #ge = GrabberElement()
    
    fields = ClassUtils.get_dataclass_fields(GrabberElement)
    print(fields)
    
def test_010():
    ge = GrabberElement()
    
    ClassUtils.set_property(ge, "id", "test_id")
    
    print(ge)