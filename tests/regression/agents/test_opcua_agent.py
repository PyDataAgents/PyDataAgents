import pytest
import time
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.buffers.DataType import DataType
from pydag.services.MappingService import MappingService
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.rest.RestService import RestService
from pydag.utils.AdapterUtils import AdapterUtils
from pydag.services.opcua.OpcUaService import OpcUaAdapter

@pytest.mark.skip(reason="Integration test requires Prosys OPC UA Simulation Server")
def test_opcua_read_temperature_loop():
    agent = Agent(id="G1")
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    opcua = OpcUaAdapter(id="A1")
    opcua.endpoint = "opc.tcp://jh:48010"
    agent.add_adapter(opcua)
    mapping = MappingService(id="M1")
    mapping.add_buffer(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.set_adapter(opcua)
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.observing_time = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    agent.add_service(mapping)
    agent.start()
    time.sleep(2)
    for _ in range(3):
        agent.get_buffer("T1").json(n=1, persistent=False)
        time.sleep(1)
    agent.stop()

@pytest.mark.skip(reason="Integration test requires Prosys OPC UA Simulation Server")
def test_opcua_get_missing_element():
    agent = Agent(id="AG1")
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    opcua = OpcUaAdapter(id="A1")
    opcua.endpoint = "opc.tcp://jh:48010"
    agent.add_adapter(opcua)
    mapping = MappingService(id="M1")
    mapping.add_buffer(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.set_adapter(opcua)
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.observing_time = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    agent.add_service(mapping)
    assert agent.get_element("N1") is None

@pytest.mark.skip(reason="Integration test requires Prosys OPC UA Simulation Server + REST port")
def test_opcua_rest_blocking_start():
    agent = Agent(id="AG1")
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    opcua = OpcUaAdapter(id="A1")
    opcua.endpoint = "opc.tcp://jh:48010"
    agent.add_adapter(opcua)
    mapping = MappingService(id="M1")
    mapping.add_buffer(buf)
    mapping.addresses = AdapterUtils.address_to_list("ns=4;s=AirConditioner_1.Temperature")
    mapping.set_adapter(opcua)
    mapping.mapping_type = MappingType.READ
    mapping.n = 1
    mapping.observing_time = 1000
    mapping.thread_type = ThreadType.MILLI_SECOND
    agent.add_service(mapping)
    rs = RestService(port=8002)
    agent.add_service(rs)
    # Do not actually block in tests; just verify start/stop
    agent.start()
    assert agent.is_running() is True
    agent.stop()
    assert agent.is_running() is False
    