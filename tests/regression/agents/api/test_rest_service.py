from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.DataType import DataType
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.agents.Agent import Agent

    
def test_010():
    agent = Agent(id = "G1")
    
    s = Sine()
    b = SignalBuffer(signal = s, capacity = 100, id = "S1", sampling_period = 100, unit = "V", data_type = DataType.FLOAT.value)
    b.install()

    agent.add_buffer(b)
    
    app = AgentApp(with_api=True, port=8108)
    app.set_agent(agent)
    app.create()
    app.run()