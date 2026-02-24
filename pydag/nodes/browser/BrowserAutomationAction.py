from dataclasses import dataclass

from ...services.Service import Service
from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...services.browser.BrowserAutomationService import BrowserAutomationService
from ..Action import Action
from ..ServiceNode import ServiceNode


@dataclass
class BrowserAutomationAction(ServiceNode, Action):
      
    def _on_install(self, agent : Agent = None):
        ServiceNode._on_install(self, agent)
        if not isinstance(self._service, BrowserAutomationService):
            raise NodeException("the specified " + self._service.cname() + " is not of instance " +  BrowserAutomationService.cname())