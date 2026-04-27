
from pydag.services.vision.WebcamService import WebcamService
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.MappingService import MappingService
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.rest.RestService import RestService


def test_webcam_agent():
    ag = Agent()
    wca = WebcamService(encode_base64=True)
    buf = ListBuffer(id="B1", data_type=DataType.IMAGE, capacity=1)
    m = MappingService(thread_type=ThreadType.INSTANT, mapping_type=MappingType.READ)
    m.set_adapter(wca)
    m.add_buffer(buf)
    rs = RestService(port=8108)
    
    ag.add_buffer(buf)
    ag.add_adapter(wca)
    ag.add_service(m)
    ag.add_service(rs)
    
    ag.release()
    