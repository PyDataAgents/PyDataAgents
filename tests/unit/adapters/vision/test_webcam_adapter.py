from pydag.adapters.vision.WebcamAdapter import WebcamAdapter
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.utils.DataUtils import DataUtils


def test_webcam_adapter():
    wca = WebcamAdapter()
    wca.install()
    
    buf = ListBuffer(data_type=DataType.IMAGE)
    buf.install()
    
    buffers = buf.to_dict()
    
    assert wca.connect(), "Could not connect Adapter"
    
    for i in range(1, 2):

        wca.read_from_source(buffers, [])
        #print(buf.data(persistent=True))    
    
    d = buf.data()
    
    DataUtils.serialize_dict(d)
    print(d)
    
    di = d["values"][0]
    
    print(di)
    
    assert wca.disconnect(), "could not disconnect adapter"
    wca.uninstall()
    buf.uninstall()
    
    