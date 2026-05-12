from pathlib import Path
from pydag.agents.AgentElement import AgentElement
from pydag.services.Service import Service
from pydag.utils.AutoDocUtils import generate_docs_for_type


def test_000():
    # find all services
    generate_docs_for_type(Service.cname() + "s", AgentElement.cname(), Path("pydag\\service"), Path("pydag\\_docs\\"))
