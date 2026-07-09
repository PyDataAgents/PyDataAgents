import json
import os
from loguru import logger
from nicegui import ui

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
    
    
def test_code_editor_ui():
    
    def _root():
        agent_config = {"name": "agent1", "temperature": 0.7}

        editor = ui.codemirror(
            value=json.dumps(agent_config, indent=2),
            language="json",
        ).classes("w-full h-64")

        def save():
            try:
                updated = json.loads(editor.value)
                print("Updated config:", updated)
            except Exception as e:
                ui.notify(f"Invalid JSON: {e}", color="red")

        ui.button("Save", on_click=save)
    
    os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", "8080")
    ui.run(root=_root, port = 8080)
