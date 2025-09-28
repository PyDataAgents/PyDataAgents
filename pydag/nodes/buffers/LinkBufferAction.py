from dataclasses import dataclass
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode

class LinkBufferAction(BufferNode, Action):
    """`Action` that's only function is to link a buffer from agent to the statemachine
    therefore an empty execute method is provided
    """
    
    def execute(self):
        return