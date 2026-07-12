from dataclasses import dataclass, field

from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...agents.AgentElement import AgentElement
from ..BufferNode import BufferNode
from ..Action import Action
from ..AgentNode import AgentNode
from ...utils.ClassUtils import ClassUtils

@dataclass
class ConfigureElementAction(AgentNode, BufferNode, Action):
    """ This `Action` configures a `AgentElement` property by the provided `element_id` and name of the `option`, which is the class' property
    <br>the new property value is derived from the `Node`'s `buffer`

    Args:
        AgentNode (_type_): inherits from class `AgentNode`
        BufferNode (_type_): inherits from class `BufferNode`
        Action (_type_): inherits the `Action` interface

    Raises:
        StatemachineException: if an error occurs during execute
    """
    
    option : str = field(init=True, default=None, metadata={"description": "option to configure with new value"})
    element_id : str = field(init=True, default=None, metadata={"description": "id of the element to change the option for"})
        
    def _on_install(self, agent : Agent = None):
        AgentNode._on_install(self, agent)
        BufferNode._on_install(self, agent)
        
    def _on_uninstall(self, agent : Agent = None):
        AgentNode._on_uninstall(self, agent)
        BufferNode._on_uninstall(self, agent)
        
    def _on_execute(self):
        data = self.get_parent_data()
        val = next(iter(data.values()))
        element = self._agent.get_element(self.element_id)
        if element is not None:
            if ClassUtils.is_property_dict(element, self.option):
                if isinstance(val, dict):
                    ClassUtils.set_property(element, self.option, val)
                    return
                else:
                    raise NodeException("Value was not a dictionary, but the property '" + self.option + "' is!")
            if ClassUtils.is_property_list(element, self.option):
                if isinstance(val, list):
                    ClassUtils.set_property(element, self.option, val)
                    return
                else:
                    raise NodeException("Value was not a list, but the property '" + self.option + "' is!")
            if isinstance(val, dict):
                if len(val) == 1:
                    ClassUtils.set_property(element, self.option, val.values()[0])
                else:
                    raise NodeException("Value  dictionary contains more than one return value for ConfigureElementAction, but should only contain one!")
            if isinstance(val, list):
                ClassUtils.set_property(element, self.option, val[0])        
        else:
            raise NodeException("No " + AgentElement.cname() + " with id=" + self.element_id + " was found")