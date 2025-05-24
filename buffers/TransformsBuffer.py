from dataclasses import dataclass, field
from PyDataGrabber.buffers.ListBuffer import ListBuffer
from PyDataGrabber.buffers.ObjectTransformation import ObjectTransformation

@dataclass
class TransformsBuffer(ListBuffer):
    """
    TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
    It is used to transform data from one format to another.
    """
    
    transformations : list[ObjectTransformation] = field(default=[], metadata = {"description": "List of transformations to apply to the data"})

    def __init__(self):
        super().__init__()
        
    def push(self, elements : list):
        transformed_elements = elements
        # Apply each transformation to the elements
        for transformation in self.transformations:
            transformed_elements = transformation.apply_n(transformed_elements)
        super().push(transformed_elements)