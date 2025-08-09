from pydag.utils.AutoDocUtils import *


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

