import multiprocessing

import uvicorn
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.services.rest.RestService import RestService

grabber = Grabber("G1")

service = RestService("S1")
service.set_grabber(grabber)

app = service.app

if __name__ == '__main__':
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False, workers=1)