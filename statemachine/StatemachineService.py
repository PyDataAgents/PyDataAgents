from dataclasses import dataclass, field
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.mappings.ObserverThread import ObserverThread
from PyDataGrabber.mappings.ThreadType import ThreadType
from PyDataGrabber.services.Service import Service
from PyDataGrabber.services.ServiceException import ServiceException
from PyDataGrabber.statemachine.Action import Action
from PyDataGrabber.statemachine.Node import Node
from PyDataGrabber.statemachine.Statemachine import Statemachine
from PyDataGrabber.statemachine.StatemachineObserver import StatemachineObserver

@dataclass
class StatemachineService(Service):
    
    start_node_id : str = field(default=None, metadata={"description": "ID of the start node in the statemachine service"})
    nodes : dict[str, Node] = field(default_factory=dict[str, Node](), metadata={"description": "dictionary of nodes in the statemachine service"})
    
    def __init__(self):
        super().__init__()
        self.statemachine : Statemachine = None
        self.observer_thread : ObserverThread = None
        self.nodes = dict[str, Node]()

    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.connect_nodes()        
    
    def start(self):
        if self.start_node_id is None:
            raise ServiceException("Start node ID must be set before starting the statemachine service.")
        if self.start_node_id not in self.nodes:
            raise ServiceException(f"Start node with ID {self.start_node_id} not found in the statemachine service.")
        if not isinstance(self.nodes[self.start_node_id], Action):
            raise ServiceException(f"Node with ID {self.start_node_id} is not a valid Action Node instance.")
        self.statemachine = Statemachine(self.nodes[self.start_node_id])
        self.observer_thread = ObserverThread(self.observer_thread.unique_id(), ThreadType.ONLY_ONCE, 0)
        observer = StatemachineObserver(self.statemachine)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()

    def stop(self):
        self.statemachine.stop()
    
    def add_node(self, node : Node):
        self.nodes[node.id] = node
        
    def connect_nodes(self):
        """
        Connect nodes in the statemachine service.
        This method should be called after all nodes have been added to the service.
        """
        for node in self.nodes.values():
            if len(node.children) == 0 and len(node.parents) == 0:
                for child_id in node.child_ids:
                    if child_id in self.nodes:
                        node.add_child(self.nodes[child_id])
                    else:
                        raise ServiceException(f"Child node with ID {child_id} not found for node {node.id}.")