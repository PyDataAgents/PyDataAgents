from ..adapters.PublishAdapter import PublishAdapter
from ..adapters.ReadAdapter import ReadAdapter
from ..adapters.SubscribeAdapter import SubscribeAdapter
from ..adapters.WriteAdapter import WriteAdapter
from .MappingException import MappingException
from .MappingType import MappingType
from .Observer import Observer
from .Mapping import Mapping

class MappingObserver(Observer):
    """abstract base class for mapping observers
    """
    
    def __post_init__(self, mapping : Mapping):
        super().__post_init__()
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