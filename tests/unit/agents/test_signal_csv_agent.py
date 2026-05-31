import os
import time
from pydag.services.csv.CsvWriteService import CsvWriteService
from pydag.agents.Agent import Agent
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType


def test_signal_csv_agent():
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
                        mapping_type=MappingType.WRITE.value,
                        n=1,
                        persistent=False)
    a.add_buffer(buf)
    
    
    ag.add_service(a)
    
    ag.release(blocking=False)
    
    time.sleep(5)
    
    ag.terminate()
    
def test_signal_csv_agent2():
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
    
    ag.release(blocking=False)
    
    time.sleep(5)
    
    ag.terminate()
