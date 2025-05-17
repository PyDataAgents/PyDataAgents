from abc import abstractmethod
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.mappings.Observer import Observer
from PyDataGrabber.src.mappings.Mapping import Mapping


class MappingObserver(Observer):
    
    def __init__(self, mapping : Mapping, id : str = None):
        super().__init__(id)
        self.mapping : Mapping = mapping    