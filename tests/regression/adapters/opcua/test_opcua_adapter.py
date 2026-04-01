import time


from pydag.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from pydag.buffers.ListBuffer import ListBuffer


def test000():
    opcua = OpcUaAdapter( id= "OPC1", endpoint="opc.tcp://jh:48010")
    print(opcua.id)
    
    buf1 = ListBuffer()
    buf1.id = "BUF1"
    buf1.capacity = 1
    buf_dict = buf1.to_dict()
    buf1.install()
    
    
    address1 = "ns=3;i=4294967295"
    address_list = list()
    address_list.append(address1)
    
    opcua.install()
    opcua.connect()
    
    n = 5
    i = 0
    while i < n:
        opcua.read_from_source(buf_dict, address_list, n=1)    
        print(buf1.data())
        time.sleep(1)
        i = i + 1

def test010():
    """
    start the opc ua simulation server before testing
    """
    opcua = OpcUaAdapter(id= "OPC1", endpoint="opc.tcp://jh:48010")
    print(opcua.id)
    
    buf1 = ListBuffer(id="T1", capacity=1)
    buf_dict = buf1.to_dict()
    buf1.install()
    
    
    address1 = "ns=4;s=AirConditioner_1.Temperature"
    address_list = list()
    address_list.append(address1)
    
    opcua.install()
    
    opcua.connect()
    
    n = 5
    i = 0
    while i < n:
        opcua.read_from_source(buf_dict, address_list, 1)    
        print(buf1.data())
        time.sleep(1)
        i = i + 1
        
        
def test_opcua_browsing():
    opcua = OpcUaAdapter(endpoint = "opc.tcp://jh:48010", id = "OPC1")
    opcua.install()
    opcua.connect()
    addresses = opcua.browse()
    for addr in addresses:
        print(addr)
        