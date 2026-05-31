import os

from pydag.agents.Agent import Agent
from pydag.services.datamodel.DataModelRestAPI import DataModelRestAPI
from pydag.services.datamodel.DataModelService import DataModelService

def test_000():
    
    agent = Agent(port=8092)
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    agent.add_service(dms)
    
    agent.create_api(no_default_apis=True)
    agent.add_api(DataModelRestAPI.get_api_router(agent))
    
    agent.release()