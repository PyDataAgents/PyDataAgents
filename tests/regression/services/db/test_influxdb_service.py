import time
import configparser
import pytest

from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.MappingService import MappingService
from pydag.services.db.InfluxDbService import InfluxDbService


def test_010():    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("INFLUX"):
        pytest.skip("Skipping InfluxDB test: missing [INFLUX] in config.ini")
    for key in ("influx_token", "influx_org"):
        if not config.has_option("INFLUX", key):
            pytest.skip(f"Skipping InfluxDB test: missing {key} in [INFLUX] of config.ini")
    
    s = Sine()
    s.f = 0.01
    sb = SignalBuffer()
    sb.signal = s
    sb.capacity=1
    sb.sampling_period=100
    
    
    address = "b=test2;m=m1;f=sine"
    address_list = MappingService.address_to_list(address)
        
    i = InfluxDbService()
    i.endpoint = "http://localhost:8086"
    i.token = config["INFLUX"]["influx_token"]
    i.org = config["INFLUX"]["influx_org"]
    i.addresses = address_list
    i.install()
    
    
    j = 0
    while j < 10:
        i.write_to_sink()
        time.sleep(0.1)
        j = j + 1
        