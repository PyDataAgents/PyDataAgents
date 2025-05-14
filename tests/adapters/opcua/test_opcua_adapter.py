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
        opcua.readFromSource(bufDict, addressList)    
        print(buf1.data())
        i = i + 1
        