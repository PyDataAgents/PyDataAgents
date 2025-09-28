from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ...nodes.Action import Action
from ...services.Service import Service


class SimpleActionObserver(Observer):
    pass


@dataclass
class SimpleActionService(Service):
     
    nodes : list[Action] = field(default_factory=list[Action], metadata={"description": "list of Action nodes to be executed in the statemachine"})
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})    
    thread_type : str = field(default=ThreadType.INSTANT.value, metadata={"description": ""})
    sampling_period : int = field(default=0, metadata={"description": "sampling period that specifies the interval the observer thread should run for"})
    
    def __post_init__(self):
        super().__post_init__()
        self.observer_thread : ObserverThread = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        for node in self.nodes:
            node.install(agent)