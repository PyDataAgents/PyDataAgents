import time
from PyDataGrabber.pydatagrabber.adapters.mqtt.MQTTAdapter import MQTTAdapter
from PyDataGrabber.pydatagrabber.buffers.ListBuffer import ListBuffer
from PyDataGrabber.pydatagrabber.utils.AdapterUtils import AdapterUtils
from PyDataGrabber.pydatagrabber.utils.BufferUtils import BufferUtils


def test_000():
    mqtt = MQTTAdapter()
    mqtt.id = "M1"    
    mqtt.endpoint = "localhost"
    mqtt.port = 1883
    
    mqtt.connect()
    
    
    buf = ListBuffer()
    buf.id = "B1"
    
    topic = "test/t1"
    address = "topic=" + topic + ";id=" + buf.id
    address_list = AdapterUtils.address_to_list(address)
    
    buf_dict = BufferUtils.to_dict(buf)
    
    mqtt.subscribe(buf_dict, address_list)
    
    i = 0
    while i < 25:        
        print(buf.data(1, False))
        time.sleep(1)
        i = i + 1
    
    
        
    
    