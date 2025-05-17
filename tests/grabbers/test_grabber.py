import time
from PyDataGrabber.src.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from PyDataGrabber.src.buffers.Buffer import DataType
from PyDataGrabber.src.buffers.ListBuffer import ListBuffer
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.mappings.Mapping import Mapping, MappingType, ThreadType
from PyDataGrabber.src.utils.AdapterUtils import AdapterUtils
from PyDataGrabber.src.utils.BufferUtils import BufferUtils


def test_000():
    grabber = Grabber("G1")
    
    buf = ListBuffer("T1")
    buf.capacity = 1
    buf.data_type = DataType.NUMERIC
    buf.unit = list("°C")
    
    grabber.add_buffer(buf)
    
    opcua = OpcUaAdapter("OPC1")
    opcua.endpoint = "opc.tcp://jh:48010"
    
    grabber.add_adapter(opcua)
    
    mapping = Mapping("M1")
    mapping.buffers = BufferUtils.to_dict(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.adapter = opcua
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.sampling_period = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    
    grabber.add_mapping(mapping)
    
    grabber.start()
    
    time.sleep(10)
    
    grabber.stop()
    