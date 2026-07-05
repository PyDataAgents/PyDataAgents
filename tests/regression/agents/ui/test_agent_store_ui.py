import os
from loguru import logger

from pydag.agents.AgentStore import AgentStore
from pydag.agents.auth.Auth import AuthManager


def test_agent_store_open():    

    # Remove default console handler (optional)
    #logger.remove()

    # Add file handler
    logger.add(
        os.path.dirname(__file__) + os.sep + "test.log",           # log file name
        rotation="10 MB",    # rotate after file reaches 10 MB
        retention="10 days", # keep logs for 10 days
        level="INFO",        # minimum log level
        format="{time} | {level} | {name}:{function}:{line} - {message}"
    )
    
    AuthManager(os.path.dirname(__file__) + os.sep + "users.yaml")
    
    ags : AgentStore = AgentStore(template_paths=[os.path.dirname(__file__)])
    ags.open()