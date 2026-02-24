from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.rest.RestService import RestService


def test_000():
    agent = Agent(description="Test agent for REST API")
   
    buf = ListBuffer(id="B1", capacity=10)
    agent.add_buffer(buf)
    
    rs = RestService(port=10019)
    agent.add_service(rs)
    
    agent.release()
    
    
    