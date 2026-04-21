from dataclasses import dataclass, field


from ..ObserverService import ObserverService


@dataclass
class MappingReconnectService(ObserverService):
    """ An `ObserverService` that attempts reconnects on failed `MappingService`'s

    Args:
        ObserverService (Service): parent class
    """

    reconnect_interval : int = field(default=10, metadata={"description": "interval in seconds, that mapping services are checked for errors and reconnect attempts"})
    reconnect_attempts : int = field(default=3, metadata={"description": "number of consecutive reconnect attempts before omitting the mapping service from reconnect attempts"})