import os

from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.services.datamodel.DataModelRestAPI import DataModelRestAPI
from pydag.services.datamodel.DataModelService import DataModelService

def test_000():
    
    agent = Agent()
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    agent.add_service(dms)
        
    app = AgentApp(port=8092, with_ui=True, with_api=True, dark_mode=False)
    app.set_agent(agent)
    app.add_ui_page(DataModelRestAPI.get_api_router(agent))
    app.create(no_default_apis=True)
    app.run()