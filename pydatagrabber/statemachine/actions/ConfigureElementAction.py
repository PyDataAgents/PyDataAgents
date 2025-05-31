from dataclasses import dataclass, field
from ...grabbers.Grabber import Grabber
from ...grabbers.GrabberElement import GrabberElement
from ..BufferNode import BufferNode
from ..GrabberNode import GrabberNode
from ..StatemachineException import StatemachineException
from ...utils.ClassUtils import ClassUtils

@dataclass
class ConfigureElementAction(GrabberNode, BufferNode):
    """this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
    <br>the new property value is derived from the `Node`'s `buffer`

    Args:
        GrabberNode (_type_): inherits from class GrabberNode
        BufferNode (_type_): inherits from class BufferNode

    Raises:
        StatemachineException: if an error occurs during execute
    """
    
    option : str = field(default=None, metadata={"description": "option to configure with new value"})
    element_id : str = field(default=None, metadata={"description": "id of the element to change the option for"})
    n : int = field(default=1, metadata={"description": "specifies the number of samples to remove from buffer"})
        
    def __init__(self):
        super().__init__()
    
    def install(self, grabber : Grabber = None):
        GrabberNode.install(self, grabber)
        BufferNode.install(self, grabber)
        
    def deinstall(self, grabber : Grabber = None):
        GrabberNode.deinstall(self, grabber)
        BufferNode.deinstall(self, grabber)
        
    def execute(self):
        val = self.buffer.data(n = self.n, persistent = False)
        element = self.grabber.get_element(self.element_id)
        if element is not None:
            ClassUtils.set_property(self, self.option, val)
        else:
            raise StatemachineException("No " + GrabberElement.cname() + " with id=" + self.element_id + " was found")