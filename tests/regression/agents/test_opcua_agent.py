import time
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.buffers.DataType import DataType
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.rest.RestService import RestService
from pydag.services.opcua.OpcUaService import OpcUaService

#Integration test requires Prosys OPC UA Simulation Server
def test_opcua_read_temperature_loop():
    agent = Agent(id="G1")
    
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    
    opcua = OpcUaService(
        id="A1",
        endpoint = "opc.tcp://jh:48010",
        addresses = ["ns=4;s=AirConditioner_1.Temperature"],
        mapping_type = MappingType.READ.value,
        n = 1,
        observing_time = 1000,
        thread_type = ThreadType.MILLI_SECOND.value
    )
    opcua.add_buffer(buf)
    
    agent.add_service(opcua)
    
    agent.release(blocking=False)
    time.sleep(2)
    for _ in range(3):
        agent.get_buffer("T1").json(n=1, persistent=False)
        time.sleep(1)
    agent.terminate()

#Integration test requires Prosys OPC UA Simulation Server
def test_opcua_get_missing_element():
    agent = Agent(id="AG1")
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    opcua = OpcUaService(
        id="A1",
        endpoint = "opc.tcp://jh:48010",
        addresses = ["ns=4;s=AirConditioner_1.Temperature"],
        mapping_type = MappingType.READ.value,
        n = 1,
        observing_time = 1000,
        thread_type = ThreadType.MILLI_SECOND.value
    )
    opcua.add_buffer(buf)
    agent.add_service(opcua)
    assert agent.get_element("N1") is None

#Integration test requires Prosys OPC UA Simulation Server + REST port
def test_opcua_rest_blocking_start():
    agent = Agent(id="AG1")
    buf = ListBuffer(id="T1", capacity=1, data_type=DataType.FLOAT.value, unit="°C")
    agent.add_buffer(buf)
    opcua = OpcUaService(
        id="A1",
        endpoint = "opc.tcp://jh:48010",
        addresses = ["ns=4;s=AirConditioner_1.Temperature"],
        mapping_type = MappingType.READ.value,
        n = 1,
        observing_time = 1000,
        thread_type = ThreadType.MILLI_SECOND.value
    )
    opcua.add_buffer(buf)
    agent.add_service(opcua)
    
    rs = RestService(port=8002)
    agent.add_service(rs)
    # Do not actually block in tests; just verify start/stop
    agent.release()
    assert agent.is_running() is True
    agent.terminate()
    assert agent.is_running() is False
    