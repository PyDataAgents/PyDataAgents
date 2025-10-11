from dataclasses import dataclass, field


from ..agents.Agent import Agent
from .transforms.Transform import Transform
from .DataElement import DataElement


@dataclass
class TransformElement(DataElement):
    """
    Base class for Transformer data elements.
    This class is intended to be extended by specific transformer implementations.
    """
    transforms : list[Transform] = field(default_factory=list, metadata={"description": "List of preprocessing transformations to apply before learning or inference."})
    
    def install(self, agent : Agent = None):
        super().install(agent)
        for transform in self.transforms:
            transform.install(agent)
               
    def execute(self):
        data, meta = self.get_data()
        transformed_data = data
        for transform in self.transforms:            
            transformed_data = transform.transform(transformed_data)
            
        self.set_data(transformed_data, None)    