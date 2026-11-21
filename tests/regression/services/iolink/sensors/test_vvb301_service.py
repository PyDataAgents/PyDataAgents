from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.sensors.VVB301Service import VVB301Service


def test_vvb301_service():
    buf = DictBuffer()    
    buf.install()

    vvb = VVB301Service(host="192.168.1.250", thread_type=ThreadType.INSTANT.value)
    vvb.add_buffer(buf)
    
    vvb.install()
    #vvb.start()
    
    vvb.read_from_source()
    
    print(buf.data())