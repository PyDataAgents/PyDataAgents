import os
import time

from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.http.HttpPutAction import HttpPutAction
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.services.datamodel.DataModelRestAPI import DataModelRestAPI

def test_000():
    
    agent = Agent(port=8092)
    
    dms = DataModelService(id="DMS1")
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    agent.add_service(dms)
    
    session_id : str = dms.create_session()
    
    agent.create_api(no_default_apis=True)
    agent.add_api(DataModelRestAPI.get_api_router(agent))
    
        
    agent.release(blocking=False)
        
    time.sleep(1)
    
    buf = DictBuffer()
    buf.install()
    buf.push({"a": 1.5})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    service_id = dms.id
    model_id = "M1"       
    http = HttpPutAction(url=f"http://localhost:{agent.port}/api/v1/datamodelservices/{service_id}/session/{session_id}/model/{model_id}")
    http.add_parent(lba)
    http.install()
    
    http.execute()
    
    print(http.get_buffer().data())
    
    agent.terminate()