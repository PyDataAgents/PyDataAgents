import os

from pydag.agents.AgentStore import AgentStore
from pydag.agents.app.AgentApp import AgentApp
from pydag.agents.auth.Auth import AuthManager
from pydag.agents.app.AgentStoreApp import AgentStoreApp
   
def test_agent_store_app():
    AuthManager(os.path.dirname(__file__) + os.sep + "users.yaml")
    
    aa1 : AgentApp = AgentApp.load(os.path.dirname(__file__) + os.sep + "sine_buffer_agent_app_template.yaml")
    aa2 : AgentApp = AgentApp.load(os.path.dirname(__file__) + os.sep + "bool_buffer_agent_app_template.yaml")
    store : AgentStore = AgentStore()
    store.add_template_from(aa1)
    store.add_template_from(aa2)
    
    asa = AgentStoreApp()
    asa.set_agent_store(store)
    asa.create()
    asa.run()  