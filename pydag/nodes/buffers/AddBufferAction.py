from dataclasses import dataclass, field
from ...buffers.Buffer import Buffer
from ..Action import Action
from ..AgentNode import AgentNode
from ...utils.ClassUtils import ClassUtils
from ..NodeException import NodeException

@dataclass
class AddBufferAction(AgentNode, Action):
    """
    Action to add a buffer to the agent node.
    """
    
    config : dict = field(default=None, metadata={"description": "Configuration for the buffer to be added."})

    def _on_execute(self):
        """
        Execute the action to add a buffer to the agent node.
        """
        if self.config is None:
            raise NodeException("Configuration for the buffer must be provided.")
        else:
            if "type" in self.config:
                buffer : Buffer = ClassUtils.create_instance(self.config["type"])
                ClassUtils.set_properties(buffer, self.config)
                self._agent.add_buffer(buffer)
            else:
                raise NodeException("Buffer type must be specified in the configuration.")
        