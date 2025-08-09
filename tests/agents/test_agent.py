import time
from pydag.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.Agent import Agent
from pydag.mappings.Mapping import Mapping
from pydag.mappings.MappingType import MappingType
from pydag.mappings.ThreadType import ThreadType
from pydag.utils.AdapterUtils import AdapterUtils
from pydag.utils.BufferUtils import BufferUtils


def test_000():
    agent = Agent()
    agent.id = "G1"
    
    buf = ListBuffer()
    buf.id = "T1"
    buf.capacity = 1
    buf.data_type = DataType.FLOAT
    buf.unit = "°C"
    
    agent.add_buffer(buf)
    
    opcua = OpcUaAdapter()
    opcua.id = "A1"
    opcua.endpoint = "opc.tcp://jh:48010"
    
    agent.add_adapter(opcua)
    
    mapping = Mapping()
    mapping.id = "M1"
    mapping.buffers = BufferUtils.to_dict(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.adapter = opcua
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.sampling_period = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    
    agent.add_mapping(mapping)
    
    agent.start()
    
    time.sleep(2)
    
    i = 0
    while i < 10:
        print(agent.get_buffer("T1").json(n = 1, persistent = False))
        time.sleep(1)
        i = i + 1
    
    agent.stop()
    
def test_010():
    """
    this test requires the installation of Prosys OPC UA Simulation Server
    https://prosysopc.com/products/opc-ua-simulation-server/evaluate/
    """
    agent = Agent()
    agent.id = "AG1"
    
    buf = ListBuffer()
    buf.id = "T1"
    buf.capacity = 1
    buf.data_type = DataType.FLOAT
    buf.unit = "°C"
    
    agent.add_buffer(buf)
    
    opcua = OpcUaAdapter()
    opcua.id = "A1"
    opcua.endpoint = "opc.tcp://jh:48010"
    
    agent.add_adapter(opcua)
    
    mapping = Mapping()
    mapping.id = "M1"
    mapping.buffers = BufferUtils.to_dict(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.adapter = opcua
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.sampling_period = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    
    agent.add_mapping(mapping)
    
    agent.get_element("N1")
    