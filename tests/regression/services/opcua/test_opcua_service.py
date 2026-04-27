import time


from pydag.services.ThreadType import ThreadType
from pydag.services.MappingType import MappingType
from pydag.services.opcua.OpcUaService import OpcUaService
from pydag.buffers.ListBuffer import ListBuffer


def test_000():
    buf1 = ListBuffer()
    buf1.id = "BUF1"
    buf1.capacity = 1
    buf1.install()
    
    
    address1 = "ns=3;i=4294967295"
    address_list = list()
    address_list.append(address1)
    
    opcua = OpcUaService( id= "OPC1", endpoint="opc.tcp://jh:48010", addresses=address_list, n=1, mapping_type=MappingType.READ.value, thread_type=ThreadType.MILLI_SECOND.value)
    opcua.add_buffer(buf1)
    print(opcua.id)
    
    opcua.install()
    
    n = 5
    i = 0
    while i < n:
        opcua._read_from_source()    
        print(buf1.data())
        time.sleep(1)
        i = i + 1

def test_010():
    """
    start the opc ua simulation server before testing
    """
    
    buf1 = ListBuffer(id="T1", capacity=1)
    buf1.install()
    
    
    address1 = "ns=4;s=AirConditioner_1.Temperature"
    address_list = list()
    address_list.append(address1)
    
    opcua = OpcUaService(id= "OPC1", endpoint="opc.tcp://jh:48010", addresses=address_list, n=1, mapping_type=MappingType.READ.value, thread_type=ThreadType.MILLI_SECOND.value)
    print(opcua.id)
    opcua.add_buffer(buf1)
    opcua.install()
        
    n = 5
    i = 0
    while i < n:
        opcua._read_from_source()    
        print(buf1.data())
        time.sleep(1)
        i = i + 1
        
        
def test_opcua_browsing():
    opcua = OpcUaService(endpoint = "opc.tcp://jh:48010", id = "OPC1", mapping_type=MappingType.READ.value, thread_type=ThreadType.MILLI_SECOND.value)
    opcua.install()
    addresses = opcua._browse()
    for addr in addresses:
        print(addr)
        