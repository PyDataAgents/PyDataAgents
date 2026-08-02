import sys
from pydag.agents.AgentModule import AgentModule
from pydag.agents.app.AgentApp import AgentApp

if __name__ == "__main__":
    #AgentModule.load_iiot_modules(skip_ads=True)      
    AgentModule.load_core_modules()
        
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        aa : AgentApp = AgentApp.load(config_file)        
        aa.create()   
        aa.run()
    else:
        print("Please provide a configuration file path as an argument.")
        sys.exit(1)
