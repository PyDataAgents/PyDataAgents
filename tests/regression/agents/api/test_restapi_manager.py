import os
import time

from pydag.agents.Agent import Agent
from pydag.agents.api.RESTAPIManager import RESTAPIManager
from pydag.agents.app.AgentApp import AgentApp
from pydag.utils.FileUtils import FileUtils


def test_api_key_generation():
    api_key_file = os.path.dirname(__file__) + os.sep + "test_API_KEYS.html"
    RESTAPIManager.generate_api_keys(api_key_file=api_key_file)    
    assert FileUtils.exists_file(api_key_file), "test_API_KEYS.html should be generated"
    
def test_rest_service_with_api_keys():
    
    ag = Agent()
            
    app = AgentApp(with_api=True, port=8108, api_key_file=os.path.dirname(__file__) + os.sep + "test_API_KEYS.html")
    app.set_agent(ag)
    app.create()
    app.run()
    
    
def test_rest_service_with_no_api_keys():    
    ag = Agent()    
    app = AgentApp(with_api=True, port=8108)
    app.set_agent(ag)
    app.create()
    app.run()
    
    