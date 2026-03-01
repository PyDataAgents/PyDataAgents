import os

from pydag.agents.Agent import Agent
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.services.datamodel.DataModelRestService import DataModelRestService

def test_000():
    
    agent = Agent()
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    agent.add_service(dms)
    
    dmrs = DataModelRestService(port=8092)
    agent.add_service(dmrs)
    
    agent.release()