import os
import time

from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.http.HttpPutAction import HttpPutAction
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.services.datamodel.DataModelRestService import DataModelRestService

def test_000():
    
    agent = Agent()
    
    dms = DataModelService(id="DMS1")
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    session_id : str = dms.create_session()
    
    agent.add_service(dms)
    
    port = 8092
    dmrs = DataModelRestService(port=8092)
    agent.add_service(dmrs)
    
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
    http = HttpPutAction(url=f"http://localhost:{port}/api/v1/datamodelservices/{service_id}/session/{session_id}/model/{model_id}")
    http.add_parent(lba)
    http.install()
    
    http.execute()
    
    print(http.get_buffer().data())
    
    agent.terminate()