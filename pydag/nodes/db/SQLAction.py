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
    data_keys : list[str] = field(default_factory=list)

    def install(self, agent : Agent = None):
        ServiceNode.install(self, agent)
        BufferNode.install(self, agent)
        Action.install(self, agent)
        if not isinstance(self.service, SQLService):
            raise NodeException("referenced service is not an instance of " + SQLService.cname())
        
    
    def execute(self):
        """Executes the SQL query defined in the `query` attribute.
            If `data_keys` are defined, the query is treated as a parameterized query and values are taken from the buffers.
        """
        # TODO
        pass