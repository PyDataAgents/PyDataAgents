import os

from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService


def test_iolink_vvb301():
    host = "https://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value)
    ios.install()
    
    print(ios._pdin_schema)
    
def test_iolink_iep200():
    host = "https://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_IEP200.xml"    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value)
    ios.install()
    
    print(ios._pdin_schema)
    
def test_iolink_vvb301_decoding():
    hex = "002D001407D003D0003200FA00000000"
    
    host = "https://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value)
    ios.install()
    
    d = ios._decode_process_data(hex, ios._pdin_schema)
    print(d)