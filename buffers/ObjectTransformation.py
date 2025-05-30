from abc import abstractmethod
from dataclasses import dataclass, field
from PyDataGrabber.buffers.DataType import DataType
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.grabbers.GrabberElement import GrabberElement

@dataclass
class ObjectTransformation(GrabberElement):
    """
    Abstract base class for object transformations for buffers
    """
    
    datatype : str = field(default=DataType.FLOAT.value, metadata={"description": "type of data expected for the transform"})
    
    def __init__(self):
        super().__init__()
        
    def install(self, grabber : Grabber = None):
        pass
    
    def deinstall(self, grabber : Grabber = None):
        pass
       
    @abstractmethod 
    def apply(self, element: any) -> any:
        """
        Apply the transformation to the data.
        
        Args:
            data (any): The data to transform.
        
        Returns:
            any: The transformed data.
        """
        
    def apply_n(self, elements: list[any]) -> list[any]:
        """
        Apply the transformation to a list of data.
        
        Args:
            data (list[any]): The data to transform.
        
        Returns:
            list[any]: The transformed data.
        """
        return [self.apply(element) for element in elements]