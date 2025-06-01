from pydatagrabber.grabbers.Grabber import Grabber
from pydatagrabber.services.rest.RestService import RestService

grabber = Grabber()
grabber.id = "G1"

service = RestService()
service.id = "S1"
service.port = 8001

grabber.add_service(service)

grabber.start_blocking()
