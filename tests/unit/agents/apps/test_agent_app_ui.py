import os

from pydag.agents.app.AgentApp import AgentApp


def test_app_with_pages():
    aa = AgentApp(with_ui=True)    
    aa.create()    
    aa.save(f"{os.path.dirname(__file__)}{os.sep}test_agent_app_ui.yaml")
    assert os.path.exists(f"{os.path.dirname(__file__)}{os.sep}test_agent_app_ui.yaml"), "the file was not created"
    
def test_load_app_with_pages():
    aa : AgentApp = AgentApp.load(f"{os.path.dirname(__file__)}{os.sep}template_agent_app_ui.yaml")
    assert len(aa.get_ui_pages()) > 0, "the app was not loaded"