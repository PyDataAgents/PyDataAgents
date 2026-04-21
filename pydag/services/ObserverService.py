from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union


from.ServiceException import ServiceException
from .ObserverException import ObserverException
from .Service import Service
from .ObserverThread import ObserverThread


if TYPE_CHECKING:
    from ..agents.Agent import Agent

@dataclass
class ObserverService(Service):
    """abstract base class for Services with ObserverThreads
    """
    
    thread_type : str = field(default=None, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ..."})    
    observing_time : Union[int|str] = field(default=None, metadata={"description": "observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ..."})    
    week_days : Optional[str] = field(default=None, metadata={"description": "specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6"})
       
    def __post_init__(self):
        super().__post_init__()
        self._observer_thread : ObserverThread = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._observer_thread = ObserverThread(service=self, observing_time=self.observing_time, thread_type=self.thread_type)        
    
    def _on_uninstall(self, agent = None):
        super()._on_uninstall(agent)
        self._observer_thread = None
        
    def _on_start(self):        
        if not self._observer_thread.is_running():
            try:
                self._observer_thread.run()
            except ObserverException as e:
                raise ServiceException(f"{Service.__name__} {self.__class__.__name__} could not run {ObserverThread.__name__}") from e
        
    def _on_stop(self):
        if self._observer_thread.is_running():
            self._observer_thread.terminate()
            
    def get_observer_thread(self) -> ObserverThread:
        return self._observer_thread
    