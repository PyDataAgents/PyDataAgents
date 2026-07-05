
import os

from pydag.agents.AgentStore import AgentStore
from pydag.agents.auth.Auth import AuthManager


def test_agent_store_open():
    AuthManager(os.path.dirname(__file__) + "/users.yaml")
    ags : AgentStore = AgentStore(template_paths=[os.path.dirname(__file__)])
    ags.open()