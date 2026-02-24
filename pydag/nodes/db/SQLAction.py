from dataclasses import dataclass, field

from ...nodes.BufferNode import BufferNode
from ...nodes.NodeException import NodeException
from ...services.db.SQLService import SQLService
from ...agents.Agent import Agent
from ...nodes.Action import Action
from ...nodes.ServiceNode import ServiceNode


@dataclass
class SQLAction(ServiceNode, BufferNode, Action):
    """`Action` node to perform SQL operations using the referenced `SQLService`.
    """
    
    query : str = field()
    
    def _on_install(self, agent : Agent = None):
        ServiceNode._on_install(self, agent)
        BufferNode._on_install(self, agent)
        if not isinstance(self._service, SQLService):
            raise NodeException("referenced service is not an instance of " + SQLService.cname())
        
    
    def _on_execute(self):
        """Executes the SQL query defined in the `query` attribute.
            If `input_keys` are defined, the query is treated as a parameterized query and values are taken from the buffers.
        """
        # TODO
        pass