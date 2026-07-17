import os
from pydag.agents.app.AgentApp import AgentApp


def test_agent_app_loading():
    file_path : str = os.path.dirname(__file__) + os.sep + "app_template.yaml"
    aa = AgentApp.load(file_path)
    print(aa)