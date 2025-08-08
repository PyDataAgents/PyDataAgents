from dataclasses import dataclass
from pydg.statemachine.Action import Action
from pydg.statemachine.BufferNode import BufferNode

class LinkBufferAction(BufferNode, Action):
    """`Action` that's only function is to link a buffer from grabber to the statemachine
    therefore an empty execute method is provided
    """
    
    def execute():
        return