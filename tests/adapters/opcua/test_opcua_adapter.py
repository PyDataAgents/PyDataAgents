import time
from PyDataGrabber.src.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from PyDataGrabber.src.buffers.ListBuffer import ListBuffer
from PyDataGrabber.src.utils.BufferUtils import BufferUtils

def test000():
    """
    start the opc ua simulation server before testing
    """
    opcua = OpcUaAdapter("OPC1")
    print(opcua.id)
    
    buf1 = ListBuffer("B1", 10)
    bufDict = BufferUtils.to_dict(buf1)
    
    opcua.endpoint("opc.tcp://jh:48010")
    
    address1 = "ns=3;i=4294967295"
    addressList = list()
    addressList.append(address1)
    
    opcua.connect()
    
    n = 1000
    i = 0
    while i < n:
        opcua.read_from_source(bufDict, addressList)    
        print(buf1.data())
        i = i + 1
        
def test010():
    """
    start the opc ua simulation server before testing
    """
    opcua = OpcUaAdapter("OPC1")
    print(opcua.id)
    
    buf1 = ListBuffer("T1", 1)
    bufDict = BufferUtils.to_dict(buf1)
    
    opcua.endpoint = "opc.tcp://jh:48010"
    
    address1 = "ns=4;s=AirConditioner_1.Temperature"
    addressList = list()
    addressList.append(address1)
    
    opcua.connect()
    
    n = 10
    i = 0
    while i < n:
        opcua.read_from_source(bufDict, addressList, 1)    
        print(buf1.data())
        time.sleep(1)
        i = i + 1
        