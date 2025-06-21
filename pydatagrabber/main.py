import sys
from pydatagrabber.grabbers.Grabber import Grabber
from pydatagrabber.grabbers.GrabberConfig import GrabberConfig
from pydatagrabber.grabbers.YAMLConfig import YAMLConfig
from pydatagrabber.services.rest.RestService import RestService

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        yc = YAMLConfig(config_file)
        gc : GrabberConfig = yc.load()
        print(gc)
        grabber = gc.create()
    else:        
        grabber = Grabber()
        grabber.id = "G1"
        service = RestService()
        service.id = "S1"
        service.port = 8001
        grabber.add_service(service)

    grabber.start_blocking()
