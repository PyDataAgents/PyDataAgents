from pathlib import Path
from pydag.adapters.Adapter import Adapter
from pydag.agents.Agent import Agent
from pydag.agents.AgentElement import AgentElement
from pydag.buffers.Buffer import Buffer
from pydag.mappings.Mapping import Mapping
from pydag.services.Service import Service
from pydag.statemachine.Action import Action
from pydag.statemachine.Transition import Transition
from pydag.utils.AutoDocUtils import generate_docs_for_type


# Run the whole process
if __name__ == "__main__":
    
    # find all agents
    generate_docs_for_type(Agent.cname() + "s", AgentElement.cname(), Path("pydag\\agents"), Path("docs\\"))
    
    # find all adapters
    generate_docs_for_type(Adapter.cname() + "s", AgentElement.cname(), Path("pydag\\adapters"), Path("docs\\"))

    # find all buffers
    generate_docs_for_type(Buffer.cname() + "s", AgentElement.cname(), Path("pydag\\buffers"), Path("docs\\"))

    # find all mappings
    generate_docs_for_type(Mapping.cname() + "s", AgentElement.cname(), Path("pydag\\mappings"), Path("docs\\"))

    # find all services
    generate_docs_for_type(Service.cname() + "s", AgentElement.cname(), Path("pydag\\services"), Path("docs\\"))
    
    # find Statemachine Nodes
    generate_docs_for_type(Action.cname() + "s and " + Transition.cname() +  "s", AgentElement.cname(), Path("pydag\\statemachine"), Path("docs\\"))

