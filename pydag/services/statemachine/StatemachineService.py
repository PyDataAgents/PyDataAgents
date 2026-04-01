from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from loguru import logger


from ...nodes.TriggerAction import TriggerAction
from ...utils.FileUtils import FileUtils
from ...services.ThreadType import ThreadType
from ..ObserverService import ObserverService
from ..ServiceException import ServiceException
from ...nodes.Node import Node

if TYPE_CHECKING:
    from ...agents.Agent import Agent
   
@dataclass
class StatemachineService(ObserverService):
    """ abstract `ObserverService` class for Statemachines

    """
    
    nodes : dict[str, Node] = field(default_factory=dict[str, Node], metadata={"description": "dictionary of nodes in the statemachine service"})
    thread_type : str = field(default=ThreadType.INSTANT.value, metadata={"description": "default thread type is INSTANT"})
    observing_time : int = field(default=0, metadata={"description": "observing time that specifies the interval the observer thread should run for"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # add children and parents first
        self.connect_nodes()
        # then install nodes
        for node in self.nodes.values():
            node.install(agent)            
            if agent.load_on_install:
                node.load_on_install = True
        # check for triggered nodes and start their trigger logic (cannot be executed before all nodes are installed)
        for node in self.nodes.values():
            if isinstance(node, TriggerAction):
                node.start_trigger()
        
    def add_node(self, node : Node):
        """
        Add a node to the statemachine service.
        
        Args:
            node (Node): The node to add.
            
        Raises:
            logger.warning: If a node with the same ID already exists.
        """
        if node.id in self.nodes:
            logger.warning(Node.cname() + " with id=" + node.id + " was already added and will not be added again")
        else:
            self.nodes[node.id] = node
        
    def remove_node(self, node_id : str):
        """
        Remove a node from the statemachine service by its ID.
        
        Args:
            node_id (str): The ID of the node to remove.
        """
        if node_id in self.nodes:
            del self.nodes[node_id] 
        
    def connect_nodes(self):
        """
        Connect nodes in the statemachine service.
        This method should be called after all nodes have been added to the service.
        """
        for node in self.nodes.values():
            if len(node.get_children()) == 0 and len(node.get_parents()) == 0:
                for child_id in node.child_ids:
                    if child_id in self.nodes:
                        node.add_child(self.nodes[child_id])
                    else:
                        raise ServiceException(f"Child node with ID {child_id} not found for node {node.id}.")
        
    def node_by_id(self, id : str) -> Node:
        """
        Retrieve a node from the statemachine service by its ID.
        
        Args:
            id (str): The ID of the node to retrieve.
            
        Returns:
            Node: The node with the specified ID, or None if not found.
        """
        if id in self.nodes:
            return self.nodes[id]
        return None
    
    def render_nodes(self, export_path : str, icon_dir : str):
        """
        Renders a the service graph using node icons and parent->child arrows.
        <br>Requires the installation of graphviz on your system. The executable 'dot' must be installed on PATH

        Args:
            export_path: Output file path (without extension)
            icon_dir: Folder containing icon images named after node class
        """
        if FileUtils.check_path("dot"):
            try:
                from graphviz import Digraph
            except ModuleNotFoundError:
                logger.error("The Python package 'graphviz' is not installed. Node graph cannot be rendered.")
                return

            icon_dir = Path(icon_dir)
            dot = Digraph(
                name="ServiceGraph",
                format="png",
                graph_attr={
                    "rankdir": "UD",
                    "bgcolor": "transparent"
                }
            )
            # --- Add nodes ---
            for node_id, node in self.nodes.items():
                class_name = node.__class__.__name__
                icon_path : Path = icon_dir / f"{class_name}.png"

                if icon_path.exists():
                    dot.node(
                        node_id,
                        label="",
                        image=str(icon_path),
                        shape="none"
                    )
                else:
                    # fallback if icon missing
                    dot.node(
                        node_id,
                        label=class_name,
                        shape="box"
                    )

            # --- Add edges (parent -> child) ---
            for node in self.nodes.values():
                for child in node.get_children():
                    dot.edge(node.id, child.id)
            
            # --- Render ---
            export_path = Path(export_path).with_suffix("")
            dot.render(export_path, cleanup=True)
            logger.debug(f"Node Graph written to {export_path}")
        else:
            logger.error("No Graphviz executable 'dot' was found on system PATH. Node graph cannot be rendered. Go to https://graphviz.org/download/")

    def save(self):
        super().save()
        # call nodes separately, so that they can individually overwrite save() and load() of `AgentElement`
        for node in self.nodes.values():
            node.save()