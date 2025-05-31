import time
from PyDataGrabber.pydatagrabber.buffers.DataType import DataType
from PyDataGrabber.pydatagrabber.buffers.SignalBuffer import SignalBuffer
from PyDataGrabber.pydatagrabber.buffers.signals.Sine import Sine
from PyDataGrabber.pydatagrabber.grabbers.Grabber import Grabber
from PyDataGrabber.pydatagrabber.services.rest.RestService import RestService

def test_000():
    grabber = Grabber()
    grabber.id = "G1"
    
    s = Sine()
    b = SignalBuffer()
    b.signal = s
    b.capacity = 100
    b.id = "S1"
    b.sampling_period = 100 # ms
    b.unit = "V"
    b.data_type = DataType.FLOAT.value

    grabber.add_buffer(b)

    service = RestService()
    service.id = "S1"
    
    grabber.add_service(service)

    grabber.start_blocking()
    
def test_010():
    grabber = Grabber()
    grabber.id = "G1"
    
    s = Sine()
    b = SignalBuffer()
    b.signal = s
    b.capacity = 100
    b.id = "S1"
    b.sampling_period = 100 # ms
    b.unit = "V"
    b.data_type = DataType.FLOAT.value

    grabber.add_buffer(b)

    service = RestService()
    service.id = "S1"
    service.install(grabber)
    
    service.start()
    
    time.sleep(5)
    
    service.stop()
