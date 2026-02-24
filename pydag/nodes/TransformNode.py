from dataclasses import dataclass, field

from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode


from ..agents.Agent import Agent
from .transforms.Transform import Transform


@dataclass
class TransformNode(BufferNode, Action):
    """
    Base class for Transformer data elements.
    This class is intended to be extended by specific transformer implementations.
    """
    transforms : list[Transform] = field(default_factory=list, metadata={"description": "List of preprocessing transformations to apply before learning or inference."})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        for transform in self.transforms:
            transform.install(agent)
               
    def _on_execute(self):
        data = self.get_parent_data()
        transformed_data = data
        for transform in self.transforms:            
            transformed_data = transform.transform(transformed_data)
            
        self.add_data(transformed_data)    