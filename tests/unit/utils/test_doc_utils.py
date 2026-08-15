from pathlib import Path
from pydag.agents.Agent import Agent
from pydag.agents.AgentElement import AgentElement
from pydag.services.Service import Service
from pydag.utils.DocUtils import generate_docs_for_type


def test_000():
    # find all services
    generate_docs_for_type(Service.cname() + "s", AgentElement.cname(), Path("pydag\\services"), Path("pydag\\_docs\\"))

def test_010():
    # find all agents
    generate_docs_for_type(Agent.__name__ + "s", AgentElement.cname(), Path("pydag\\agents"), Path("pydag\\_docs\\"))
