import os
import time

from pydag.agents.Agent import Agent
from pydag.services.rest.RESTAPIManager import RESTAPIManager
from pydag.utils.FileUtils import FileUtils
from pydag.services.rest.RestService import RestService


def test_api_key_generation():
    api_key_file = os.path.dirname(__file__) + os.sep + "test_API_KEYS.html"
    RESTAPIManager.generate_api_keys(api_key_file=api_key_file)    
    assert FileUtils.exists_file(api_key_file), "test_API_KEYS.html should be generated"
    
def test_rest_service_with_api_keys():
    
    ag = Agent()
    
    service = RestService(port=8002, api_key_file=os.path.dirname(__file__) + os.sep + "test_API_KEYS.html")
    
    ag.add_service(service)
        
    ag.release(blocking=False)
    
    time.sleep(3)
    
    ag.terminate()
    
    
def test_rest_service_with_no_api_keys():
    
    ag = Agent()
    
    service = RestService(port=8002)
    
    ag.add_service(service)
        
    ag.release(blocking=False)
    
    time.sleep(3)
    
    ag.terminate()
    
    