from dataclasses import dataclass, field
from ...agents.Agent import Agent
from ...agents.AgentElement import AgentElement
from ..BufferNode import BufferNode
from ..AgentNode import AgentNode
from ...services.statemachine.StatemachineException import StatemachineException
from ...utils.ClassUtils import ClassUtils

@dataclass
class ConfigureElementAction(AgentNode, BufferNode):
    """this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
    <br>the new property value is derived from the `Node`'s `buffer`

    Args:
        GrabberNode (_type_): inherits from class GrabberNode
        BufferNode (_type_): inherits from class BufferNode

    Raises:
        StatemachineException: if an error occurs during execute
    """
    
    option : str = field(init=True, default=None, metadata={"description": "option to configure with new value"})
    element_id : str = field(init=True, default=None, metadata={"description": "id of the element to change the option for"})
    extract_key : str = field(default=None, metadata={"description": "specifies the key to extract from parent buffer, if no key is specified, the value for the new config option is selected based on buffer data"})
        
    def install(self, agent : Agent = None):
        AgentNode.install(self, agent)
        BufferNode.install(self, agent)
        
    def uninstall(self, agent : Agent = None):
        AgentNode.uninstall(self, agent)
        BufferNode.uninstall(self, agent)
        
    def execute(self):
        val = self.buffer.data(n = self.n, persistent = self.persistent)
        if self.extract_key is not None:
            val = val[self.extract_key]
        element = self.agent.get_element(self.element_id)
        if element is not None:
            if ClassUtils.is_property_dict(element, self.option):
                if isinstance(val, dict):
                    ClassUtils.set_property(element, self.option, val)
                    return
                else:
                    raise StatemachineException("Value was not a dictionary, but the property '" + self.option + "' is!")
            if ClassUtils.is_property_list(element, self.option):
                if isinstance(val, list):
                    ClassUtils.set_property(element, self.option, val)
                    return
                else:
                    raise StatemachineException("Value was not a list, but the property '" + self.option + "' is!")
            if isinstance(val, dict):
                if len(val) == 1:
                    ClassUtils.set_property(element, self.option, val.values()[0])
                else:
                    raise StatemachineException("Value  dictionary contains more than one return value for ConfigureElementAction, but should only contain one!")
        else:
            raise StatemachineException("No " + AgentElement.cname() + " with id=" + self.element_id + " was found")