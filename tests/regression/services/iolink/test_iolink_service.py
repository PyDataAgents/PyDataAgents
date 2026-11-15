import os
import time

from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService
    
def test_iolink_service_read_from_source():    
    d = DictBuffer()
    d.install()
    
    host = "http://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"
    scaling = {"Temperature": 0.1, "Fatigue (v-RMS)": 0.0001, "Friction (a-RMS)": 0.01}    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value, scaling=scaling)
    ios.add_buffer(d)
    ios.install()
    
    print(ios._pdin_schema)
    
    for i in range(10):
        ios.read_from_source()
        
        print(d.data(persistent=False, n=1))
        time.sleep(0.1)