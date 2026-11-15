import os

from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService
    
def test_iolink_service_read_from_source():
    # TODO
    
    d = DictBuffer()
    d.install()
    
    host = "https://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value)
    ios.add_buffer(d)
    ios.install()
    
    ios.read_from_source()
    
    print(d.data())