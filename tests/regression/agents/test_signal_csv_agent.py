import os
from pydag.agents.app.AgentApp import AgentApp
from pydag.services.csv.CsvWriteService import CsvWriteService
from pydag.agents.Agent import Agent
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.ThreadType import ThreadType

def test_signal_csv_agent_rest():
    ag = Agent()
    
    s = Sine()
    buf = SignalBuffer(signal=s, capacity=1000, sampling_period=100)
    
    ag.add_buffer(buf)
    
    folder = os.path.dirname(__file__) + os.sep + "data"
    a = CsvWriteService(folder=folder,
                        file_post_fix="test",
                        max_samples=50,
                        observing_time=150,
                        thread_type=ThreadType.MILLI_SECOND.value,
                        n=1,
                        persistent=False)    
    a.add_buffer(buf)
    
    ag.add_service(a)
    
    app = AgentApp(with_api=True, port=8001)
    app.set_agent(ag)
    app.create()
    app.run()
    
