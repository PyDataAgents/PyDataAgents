import time

from pydag.agents.Agent import Agent
from pydag.buffers.ListBuffer import ListBuffer


def test_000():
    agent = Agent(description="Test agent for REST API", port=10019, with_api=True)
   
    buf = ListBuffer(id="B1", capacity=10)
    agent.add_buffer(buf)
    
    agent.release()
    
    