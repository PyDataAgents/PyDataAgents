from __future__ import annotations
from dataclasses import dataclass


from ...agents.AgentKeywords import AgentKeywords
from ...utils.FileUtils import FileUtils
from ...agents.AgentElement import AgentElement
from ..Observer import Observer
from ..ObserverService import ObserverService


class PersistObserver(Observer):
    
    def __init__(self, service: AgentPersistService):
        self._service : AgentPersistService = service

    def observe(self):
        if self._service.get_agent():
            for buffer in self._service.get_agent().buffer_store.values():
                if isinstance(buffer, AgentElement):
                    if buffer.load_on_install:
                        buffer.save(self._service.get_agent().save_folder)
            for service in self._service.get_agent().service_store.values():
                if isinstance(service, AgentElement):
                    if service.load_on_install:
                        service.save(self._service.get_agent().save_folder)

    def unobserve(self):
        return

@dataclass
class AgentPersistService(ObserverService):
    """ `ObserverService` for continuously persisting `AgentElement` configurations to filesystem
    """
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        observer = PersistObserver(self)
        self.add_observer(observer)
        if not FileUtils.exists_folder(self.get_agent().save_folder):
            FileUtils.create_dir(self.get_agent().save_folder)

