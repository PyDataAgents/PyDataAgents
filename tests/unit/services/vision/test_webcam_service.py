from pydag.services.ThreadType import ThreadType
from pydag.services.vision.WebcamService import WebcamService
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.utils.DataUtils import DataUtils


def test_webcam_adapter():
    buf = ListBuffer(data_type=DataType.IMAGE)
    buf.install()
    
    wcs = WebcamService(thread_type=ThreadType.MILLI_SECOND.value)
    wcs.add_buffer(buf)
    wcs.install()
    
        
    
    for i in range(1, 2):

        wcs._read_from_source()
        #print(buf.data(persistent=True))    
    
    d = buf.data()
    
    DataUtils.serialize_dict(d)
    print(d)
    
    di = d["values"][0]
    
    print(di)
    
    wcs.uninstall()
    buf.uninstall()
    
    