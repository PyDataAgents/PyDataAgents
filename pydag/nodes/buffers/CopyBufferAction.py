from dataclasses import dataclass
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode


@dataclass
class CopyBufferAction(BufferNode, Action):
    pass