from .Agent import Agent


class AgentStore:
    
    def __init__(self):
        self._user_store : dict[str, list[str]] = dict()
        self._agent_store : dict[str, Agent] = dict()
        self._template_store : dict[str, Agent] = dict()
                
    def load_templates(self):
        pass
    
    def add_user(self, user : str):
        pass
    
    def add_agent(self, user : str, agent : Agent):
        pass
    
    def release_agent(self, agent : Agent):
        pass
    
    def terminate_agent(self, agent : Agent):
        pass
    
