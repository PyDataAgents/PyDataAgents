import time

import pytest
from pydag.services.MappingService import MappingService
from pydag.services.MappingType import MappingType
from pydag.services.mqtt.MQTTService import MQTTService
from pydag.buffers.ListBuffer import ListBuffer

def test_000():
       
    buf = ListBuffer()
    buf.id = "B1"
    buf.install()
    
    topic = "test/t1"
    address = "topic=" + topic + ";id=" + buf.id
    address_list = MappingService.address_to_list(address)
        
    mqtt = MQTTService(id="M1",
                       endpoint="localhost",
                       port=1883,
                       addresses=address_list,
                       n=1,
                       force_numeric=True,
                       mapping_type=MappingType.SUB.value)  
    mqtt.add_buffer(buf)
    mqtt.install()
    
    mqtt.subscribe()
    
    i = 0
    while i < 25:
        print(buf.data(1, False))
        time.sleep(1)
        i = i + 1