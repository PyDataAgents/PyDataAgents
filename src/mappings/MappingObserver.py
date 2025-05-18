from PyDataGrabber.src.adapters.PublishAdapter import PublishAdapter
from PyDataGrabber.src.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.src.adapters.SubscribeAdapter import SubscribeAdapter
from PyDataGrabber.src.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.src.mappings.MappingException import MappingException
from PyDataGrabber.src.mappings.MappingType import MappingType
from PyDataGrabber.src.mappings.Observer import Observer
from PyDataGrabber.src.mappings.Mapping import Mapping

class MappingObserver(Observer):
    """abstract base class for mapping observers
    """
    
    def __init__(self, mapping : Mapping):
        super().__init__()
        self.mapping : Mapping = mapping
        self.check_mapping()
    
    def check_mapping(self):
        match self.mapping.mapping_type:
            case MappingType.READ:
                if not issubclass(self.mapping.adapter.__class__, ReadAdapter):
                    raise MappingException("adapter must be of type " + ReadAdapter.__name__)
            case MappingType.WRITE:
                if not issubclass(self.mapping.adapter.__class__, WriteAdapter):
                    raise MappingException("adapter must be of type " + WriteAdapter.__name__)
            case MappingType.SUB:
                if not issubclass(self.mapping.adapter.__class__, SubscribeAdapter):
                    raise MappingException("adapter must be of type " + SubscribeAdapter.__name__) 
            case MappingType.PUB:
                if not issubclass(self.mapping.adapter.__class__, PublishAdapter):
                    raise MappingException("adapter must be of type " + PublishAdapter.__name__)            