import time
from pydag.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from pydag.buffers.ListBuffer import ListBuffer

def test000():
    """
    start the opc ua simulation server before testing
    """
    opcua = OpcUaAdapter()
    opcua.id = "OPC1"
    print(opcua.id)
    
    buf1 = ListBuffer()
    buf1.id = "BUF1"
    buf1.capacity = 1
    buf_dict = buf1.to_dict()
    
    opcua.endpoint("opc.tcp://jh:48010")
    
    address1 = "ns=3;i=4294967295"
    address_list = list()
    address_list.append(address1)
    
    opcua.connect()
    
    n = 1000
    i = 0
    while i < n:
        opcua.read_from_source(buf_dict, address_list)    
        print(buf1.data())
        i = i + 1
        
def test010():
    """
    start the opc ua simulation server before testing
    """
    opcua = OpcUaAdapter()
    opcua.id = "OPC1"
    print(opcua.id)
    
    buf1 = ListBuffer()
    buf1.id = "T1"
    buf1.capacity = 1
    buf_dict = buf1.to_dict()
    
    opcua.endpoint = "opc.tcp://jh:48010"
    
    address1 = "ns=4;s=AirConditioner_1.Temperature"
    address_list = list()
    address_list.append(address1)
    
    opcua.connect()
    
    n = 10
    i = 0
    while i < n:
        opcua.read_from_source(buf_dict, address_list, 1)    
        print(buf1.data())
        time.sleep(1)
        i = i + 1
        