import sys
from pydag.agents.Agent import Agent
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.AgentModule import AgentModule
from pydag.agents.YAMLConfig import YAMLConfig

if __name__ == "__main__":
    #AgentModule.load_iiot_modules(skip_ads=True)      
    AgentModule.load_core_modules()
        
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        yc = YAMLConfig(config_file)
        gc : AgentConfig = yc.load()
        print(gc)
        agent = gc.create()
    else:
        agent = Agent(id = "A1")

    agent.release()
