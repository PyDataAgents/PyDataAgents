
from pydag.services.vision.WebcamService import WebcamService
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType


def test_webcam_agent():
    ag = Agent(with_api=True, port=8108)
    
    buf = ListBuffer(id="B1", data_type=DataType.IMAGE, capacity=1)
    ag.add_buffer(buf)
    
    wca = WebcamService(
        encode_base64=True,
        thread_type=ThreadType.INSTANT,
        mapping_type=MappingType.READ
    )
    wca.add_buffer(buf)
    ag.add_service(wca)
    
    ag.release()
    