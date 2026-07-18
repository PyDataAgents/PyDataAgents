import os

from pydag.agents.app.AgentApp import AgentApp


def test_agent_app():
    file_path = os.path.dirname(__file__) + os.sep + "csv_agent_app_template.yaml"
    aa = AgentApp.load(file_path)
    aa.create()
    aa.run()