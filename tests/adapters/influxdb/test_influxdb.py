import configparser
import time

from PyDataGrabber.src.adapters.influxdb.InfluxDbAdapter import InfluxDbAdapter
from PyDataGrabber.src.buffers.SignalBuffer import SignalBuffer
from PyDataGrabber.src.buffers.signals.Sine import Sine
from PyDataGrabber.src.utils.AdapterUtils import AdapterUtils
from PyDataGrabber.src.utils.BufferUtils import BufferUtils
    
def test_000():
    

    config = configparser.ConfigParser()
    config.read("config.ini")
    
    print(config["INFLUX"]["influx_user"])
    
    
def test_010():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
        
    i = InfluxDbAdapter()
    i.endpoint = "http://localhost:8086"
    i.token = config["INFLUX"]["influx_token"]
    i.org = config["INFLUX"]["influx_org"]
    
    assert i.connect() == True
    
    s = Sine()
    s.f = 0.01
    sb = SignalBuffer(s, capacity=1, sampling_period=100)
    
    d = BufferUtils.to_dict(sb)
    address = "b=test2;m=m1;f=sine"
    address_list = AdapterUtils.address_to_list(address)
    
    j = 0
    while j < 1000:
        i.write_to_sink(d, address_list, 1, False)
        time.sleep(0.1)
        j = j + 1
        
    i.disconnect()
        
    
    
    
    