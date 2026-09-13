from dataclasses import dataclass


from ..ServiceNode import ServiceNode
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class OutlookMeetingAction(BufferNode, ServiceNode, Action):
    pass