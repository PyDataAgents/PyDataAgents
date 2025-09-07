import configparser
import time

from pydag.adapters.influxdb.InfluxDbAdapter import InfluxDbAdapter
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.utils.AdapterUtils import AdapterUtils
    
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
    sb = SignalBuffer()
    sb.signal = s
    sb.capacity=1
    sb.sampling_period=100
    
    d = sb.to_dict()
    address = "b=test2;m=m1;f=sine"
    address_list = AdapterUtils.address_to_list(address)
    
    j = 0
    while j < 1000:
        i.write_to_sink(d, address_list, 1, False)
        time.sleep(0.1)
        j = j + 1
        
    i.disconnect()
        
    
    
    
    