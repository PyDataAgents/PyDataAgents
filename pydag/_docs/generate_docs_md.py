from pathlib import Path
from pydag.adapters.Adapter import Adapter
from pydag.agents.Agent import Agent
from pydag.agents.AgentElement import AgentElement
from pydag.buffers.Buffer import Buffer
from pydag.services.Service import Service
from pydag.nodes.Action import Action
from pydag.nodes.Transition import Transition
from pydag.utils.AutoDocUtils import generate_docs_for_type


# Run the whole process
if __name__ == "__main__":
    
    # find all agents
    generate_docs_for_type(Agent.__name__ + "s", AgentElement.__name__, Path("pydag\\agents"), Path("pydag\\_docs\\"))
    
    # find all adapters
    generate_docs_for_type(Adapter.__name__ + "s", AgentElement.__name__, Path("pydag\\adapters"), Path("pydag\\_docs\\"), with_images=True)

    # find all buffers
    generate_docs_for_type(Buffer.__name__ + "s", AgentElement.__name__, Path("pydag\\buffers"), Path("pydag\\_docs\\"), with_images=True)

    # find all services
    generate_docs_for_type(Service.__name__ + "s", AgentElement.__name__, Path("pydag\\services"), Path("pydag\\_docs\\"), with_images=True)
    
    # find Statemachine Nodes
    generate_docs_for_type(Action.__name__ + "s and " + Transition.__name__ +  "s", AgentElement.__name__, Path("pydag\\nodes"), Path("pydag\\_docs\\"), with_images=True)