from dataclasses import dataclass


from ...services.ThreadType import ThreadType
from ..NodeException import NodeException
from ...services.ObserverService import ObserverService
from ...agents.Agent import Agent
from ..TriggerAction import TriggerAction
from ..ServiceNode import ServiceNode


@dataclass
class ObserverTriggerAction(ServiceNode, TriggerAction):
    """ A `TriggerAction`, that connects to a `ObserverService` and executes the `Observer` notification everytime the
    trigger event occurs. This `Node` does not define `start_trigger`, but rather expects being triggered externally from application or for example REST API.
    """
       
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # check for ObserverService
        if isinstance(self._service, ObserverService):
            # check for triggered observerthread
            if self._service.thread_type != ThreadType.TRIGGERED.value:
                raise NodeException(f"{self.cname()} must be connected to an {ObserverService.cname()} with {ThreadType.__class__.__name__}={ThreadType.TRIGGERED.value}")
        else:
            raise NodeException(f"{self.cname()} must be connected to an {ObserverService.cname()}")
      
    
    def _on_trigger(self):
        if isinstance(self._service, ObserverService):
            self._service.notify_observers()
            
    def start_trigger(self):
        """ Base `TriggerNode` that does nothing during `start_trigger`, but can be used via API to trigger events
        """
        return