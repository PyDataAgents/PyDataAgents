import time
from ...pydatagrabber.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from ...pydatagrabber.buffers.DataType import DataType
from ...pydatagrabber.buffers.ListBuffer import ListBuffer
from ...pydatagrabber.grabbers.Grabber import Grabber
from ...pydatagrabber.mappings.Mapping import Mapping
from ...pydatagrabber.mappings.MappingType import MappingType
from ...pydatagrabber.mappings.ThreadType import ThreadType
from ...pydatagrabber.utils.AdapterUtils import AdapterUtils
from ...pydatagrabber.utils.BufferUtils import BufferUtils


def test_000():
    grabber = Grabber()
    grabber.id = "G1"
    
    buf = ListBuffer()
    buf.id = "T1"
    buf.capacity = 1
    buf.data_type = DataType.FLOAT
    buf.unit = "°C"
    
    grabber.add_buffer(buf)
    
    opcua = OpcUaAdapter()
    opcua.id = "A1"
    opcua.endpoint = "opc.tcp://jh:48010"
    
    grabber.add_adapter(opcua)
    
    mapping = Mapping()
    mapping.id = "M1"
    mapping.buffers = BufferUtils.to_dict(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.adapter = opcua
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.sampling_period = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    
    grabber.add_mapping(mapping)
    
    grabber.start()
    
    time.sleep(2)
    
    i = 0
    while i < 10:
        print(grabber.get_buffer("T1").json(n = 1, persistent = False))
        time.sleep(1)
        i = i + 1
    
    grabber.stop()
    
def test_010():
    grabber = Grabber()
    grabber.id = "G1"
    
    buf = ListBuffer()
    buf.id = "T1"
    buf.capacity = 1
    buf.data_type = DataType.FLOAT
    buf.unit = "°C"
    
    grabber.add_buffer(buf)
    
    opcua = OpcUaAdapter()
    opcua.id = "A1"
    opcua.endpoint = "opc.tcp://jh:48010"
    
    grabber.add_adapter(opcua)
    
    mapping = Mapping()
    mapping.id = "M1"
    mapping.buffers = BufferUtils.to_dict(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.adapter = opcua
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.sampling_period = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    
    grabber.add_mapping(mapping)
    
    grabber.get_element("N1")
    