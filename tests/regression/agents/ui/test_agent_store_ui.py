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
    
thread_loggers = {}

def _thread_logger_sink(message):
    record = message.record
    thread_id = record["thread"].id

    # Create a logger for this thread if not exists
    if thread_id not in thread_loggers:
        file_name = f"{os.path.dirname(__file__)}{os.sep}logs{os.sep}test_thread_{thread_id}.log"
        thread_loggers[thread_id] = open(file_name, "a")

    # Write log to corresponding file
    thread_loggers[thread_id].write(message)
    thread_loggers[thread_id].flush()    
    
def test_agent_store_open2():
    # Add file handler
    logger.add(
        _thread_logger_sink,
        format="{time} | {level} | {name}:{function}:{line} - {message}"
    )
    
    AuthManager(os.path.dirname(__file__) + os.sep + "users.yaml")
    
    ags : AgentStore = AgentStore(template_paths=[os.path.dirname(__file__)])
    ags.open()
