from dataclasses import dataclass, field
from ....buffers.Buffer import Buffer
from ...Action import Action
from ...AgentNode import AgentNode
from ...StatemachineException import StatemachineException
from ....utils.ClassUtils import ClassUtils

@dataclass
class AddBufferAction(AgentNode, Action):
    """
    Action to add a buffer to the agent node.
    """
    
    config : dict = field(default=None, metadata={"description": "Configuration for the buffer to be added."})

    def execute(self):
        """
        Execute the action to add a buffer to the agent node.
        """
        if self.config is None:
            raise StatemachineException("Configuration for the buffer must be provided.")
        else:
            if "type" in self.config:
                buffer : Buffer = ClassUtils.create_instance(self.config["type"])
                ClassUtils.set_properties(buffer, self.config)
                self.agent.add_buffer(buffer)
            else:
                raise StatemachineException("Buffer type must be specified in the configuration.")
        