from __future__ import annotations
import threading
#from collections import deque
from dataclasses import dataclass, field
from nicegui import ui
import os
from loguru import logger

from pydag.services.ui.UIAgentMgmtPage import UIAgentMgmtPage

from .UIBufferPage import UIBufferPage
from .UIElements import UIPage
from ..Service import Service

@dataclass
class UIService(Service):
    """ A `Service` class that auto generates a web ui based on NiceGUI """
    
    host: str = field(default="localhost", metadata={"description": "host of the NiceGUI server"})
    port: int = field(default=8081, metadata={"description": "port of the NiceGUI server"})
    title : str = field(default=None, metadata={"description": "dashboard title"})
    with_buffer_ui : bool = field(default=True, metadata={"description": "creates a ui page for buffer visualization"})
    with_mgmt_ui : bool = field(default=True, metadata={"description": "creates a ui page for agent management"}) 
    
    def __post_init__(self):
        super().__post_init__()
        self._thread : threading.Thread = None
        self._pages : list[UIPage] = []

    def _on_install(self, agent=None):
        super()._on_install(agent)
        os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
        if self.with_buffer_ui:
            self.add_page(UIBufferPage(self, 1.0 / 30.0))
        if self.with_mgmt_ui:
            self.add_page(UIAgentMgmtPage(self, 1.0))

    def _on_start(self):
        self._thread = threading.Thread(target=self._run_ui_server, daemon=True)
        self._thread.start()
        pages_paths = [f"http://{self.host}:{self.port}{page.path}" for page in self._pages]
        pages_str = "\n".join(pages_paths)
        logger.info("Available NiceGui Pages:\n" + pages_str)

    def _on_stop(self):
        #app.shutdown()
        #self._thread.join()
        return
    
    def add_page(self, page : UIPage):
        self._pages.append(page)
        
    def remove_page(self, i : int):
        self._pages.pop(i)
        
    def clear_pages(self):
        self._pages.clear()
    
    def _run_ui_server(self):
        ui.run(host=self.host, port=self.port, reload=False, root=self._create_pages)
        
    def _create_pages(self):
        # define default color schema
        ui.colors(
            primary='#005B95',
            secondary='#A8A8A9',
            accent='#C43726',
            positive='#00B050',
            negative='#C43726',
        )
        page : UIPage
        for page in self._pages:
            page.register()
    