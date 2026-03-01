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
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    agent.add_service(dms)
    
    dmrs = DataModelRestService(port=8092)
    agent.add_service(dmrs)
    
    agent.release(blocking=False)
        
    time.sleep(3)
    
    buf = DictBuffer()
    buf.push({"a": 1.5})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    service_id = dms.id
    model_id = "M1"       
    http = HttpPutAction(url=f"http://localhost:8092/api/v1/datamodelservices/{service_id}/models/{model_id}", by_rows=True)
    http.add_parent(lba)
    http.install()
    
    http.execute()
    
    print(http.get_buffer().data())
    
    agent.terminate()