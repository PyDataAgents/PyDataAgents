import os

from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService


def test_iolink_vvb301():
    host = "https://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.zip"    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value)
    ios.install()
    
    print(ios._pdin_schema)