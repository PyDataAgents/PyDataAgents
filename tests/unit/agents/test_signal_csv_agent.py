import os
import time
from pydag.adapters.csv.CsvWriteAdapter import CsvWriteAdapter
from pydag.agents.Agent import Agent
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.services.mappings.MappingService import MappingService
from pydag.services.mappings.MappingType import MappingType
from pydag.services.ThreadType import ThreadType


def test_signal_csv_agent():
    ag = Agent()
    
    s = Sine()
    buf = SignalBuffer(signal=s, capacity=1000, sampling_period=100)
    
    ag.add_buffer(buf)
    
    folder = os.path.dirname(__file__) + os.sep + "data"
    a = CsvWriteAdapter(folder=folder, file_post_fix="test", max_samples=50)
    ag.add_adapter(a)
    
    m = MappingService(observing_time=150,
                thread_type=ThreadType.MILLI_SECOND.value,
                mapping_type=MappingType.WRITE.value,
                n=1,
                persistent=False)    
    m.set_adapter(a)
    m.add_buffer(buf)
    
    ag.add_service(m)
    
    ag.release(blocking=False)
    
    time.sleep(10)
    
    ag.terminate()
    
def test_signal_csv_agent2():
    ag = Agent()
    
    s = Sine()
    buf = SignalBuffer(signal=s, capacity=1000, sampling_period=100)
    
    ag.add_buffer(buf)
    
    folder = os.path.dirname(__file__) + os.sep + "data"
    a = CsvWriteAdapter(folder=folder, file_post_fix="test", max_samples=50)
    ag.add_adapter(a)
    
    m = MappingService(observing_time=150,
                thread_type=ThreadType.MILLI_SECOND.value,
                n=1,
                persistent=False)    
    m.set_adapter(a)
    m.add_buffer(buf)
    
    ag.add_service(m)
    
    ag.release(blocking=False)
    
    time.sleep(10)
    
    ag.terminate()