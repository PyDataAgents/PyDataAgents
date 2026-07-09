from dataclasses import dataclass

from fastapi import FastAPI


from ..AgentConfig import AgentConfig
from ..Agent import Agent


@dataclass
class AgentApp():
    """ Application that stores an `Agent` and provides REST API and UI based on configuration settings """
    
        
    def __init__(self):
        self._app : FastAPI = None
        self._agent : Agent = None
    
    def set_agent(self, ag : Agent):
        self._agent = ag
        
    def load(self, file_path : str):
        ac : AgentConfig = AgentConfig.from_file(file_path)
        self._agent = ac.create()