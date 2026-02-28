from pathlib import Path
from pydag.adapters.Adapter import Adapter
from pydag.agents.AgentElement import AgentElement
from pydag.utils.AutoDocUtils import generate_docs_for_type


def test_000():
    # find all adapters
    generate_docs_for_type(Adapter.cname() + "s", AgentElement.cname(), Path("pydag\\adapters"), Path("pydag\\_docs\\"))