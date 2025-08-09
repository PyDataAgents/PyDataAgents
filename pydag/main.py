import sys
from pydag.agents.Agent import Agent
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.services.rest.RestService import RestService

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        yc = YAMLConfig(config_file)
        gc : AgentConfig = yc.load()
        print(gc)
        grabber = gc.create()
    else:        
        grabber = Agent()
        grabber.id = "G1"
        service = RestService()
        service.id = "S1"
        service.port = 8001
        grabber.add_service(service)

    grabber.start_blocking()
