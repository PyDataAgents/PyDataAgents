import os

from pydag.agents.AgentStore import AgentStore


def test_agent_template_loading():
    ags : AgentStore = AgentStore(template_paths=[os.path.dirname(__file__)])
    ags.load_templates()
    print(ags.get_templates())
    
    