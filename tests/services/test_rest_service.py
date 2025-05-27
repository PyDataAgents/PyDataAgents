import multiprocessing

import uvicorn
from PyDataGrabber.buffers.DataType import DataType
from PyDataGrabber.buffers.SignalBuffer import SignalBuffer
from PyDataGrabber.buffers.signals.Sine import Sine
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.services.rest.RestService import RestService

def test_000():
    grabber = Grabber()
    grabber.id = "G1"
    
    s = Sine()
    b = SignalBuffer(s)
    b.capacity = 100
    b.id = "S1"
    b.sampling_period = 100 # ms
    b.unit = "V"
    b.data_type = DataType.FLOAT.value

    grabber.add_buffer(b)

    service = RestService()
    service.id = "S1"
    service.set_grabber(grabber)

    app = service.app

    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False, workers=1)