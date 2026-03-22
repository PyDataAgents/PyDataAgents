from __future__ import annotations
from dataclasses import dataclass


from ...agents.AgentElement import AgentElement
from ..Observer import Observer
from ..ObserverService import ObserverService


class PersistObserver(Observer):
    
    def __init__(self, service: AgentPersistService):
        super().__init__()
        self._service : AgentPersistService = service

    def observe(self):
        if self._service.get_agent():
            for k, buffer in self._service.get_agent().buffer_store:
                if isinstance(buffer, AgentElement):
                    if buffer.load_on_install:
                        buffer.save()
            for k, adapter in self._service.get_agent().adapter_store:
                if isinstance(adapter, AgentElement):
                    if adapter.load_on_install:
                        adapter.save()       
            for k, service in self._service.get_agent().service_store:
                if isinstance(service, AgentElement):
                    if service.load_on_install:
                        service.save()  

    def unobserve(self):
        return

@dataclass
class AgentPersistService(ObserverService):
    """ `ObserverService` for continuously persisting `AgentElement` configurations to filesystem
    """
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        observer = PersistObserver(self)
        self._observer_thread.add_observer(observer) 

