from dataclasses import dataclass, field
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.statemachine.Action import Action
from PyDataGrabber.src.statemachine.GrabberNode import GrabberNode
from PyDataGrabber.src.statemachine.StatemachineException import StatemachineException
from PyDataGrabber.src.utils.ClassUtils import ClassUtils

@dataclass
class AddBufferAction(GrabberNode, Action):
    """
    Action to add a buffer to the grabber node.
    """
    
    config : dict = field(default=None, metadata={"description": "Configuration for the buffer to be added."})

    def __init__(self):
        """
        Initialize the AddBufferAction with a grabber node and buffer name.
        """
        super().__init__()

    def execute(self):
        """
        Execute the action to add a buffer to the grabber node.
        """
        if self.config is None:
            raise StatemachineException("Configuration for the buffer must be provided.")
        else:
            if "type" in self.config:
                buffer : Buffer = ClassUtils.create_instance(self.config["type"])
                ClassUtils.set_properties(buffer, self.config)
                self.grabber.add_buffer(buffer)
            else:
                raise StatemachineException("Buffer type must be specified in the configuration.")
        