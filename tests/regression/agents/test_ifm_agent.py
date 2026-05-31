from pydag.services.socket.ifmvse.VSEService import VSEService
from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer


def test_000():
    
    ag = Agent(with_api=True, port=8089)
    
    buf = ListBuffer(id="S1", capacity=300000, duplicate_ids=["S11"])    
    ag.add_buffer(buf)
    
    vse = VSEService(host="192.168.0.10", port=3321, sensor = 1, sample_rate = 100000)
    vse.add_buffer(buf)
    ag.add_service(vse)
    
    ag.release()
    
    