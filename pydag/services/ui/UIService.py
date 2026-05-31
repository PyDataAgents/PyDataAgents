from __future__ import annotations
import threading
#from collections import deque
from dataclasses import dataclass, field
from nicegui import app, ui
import os
from loguru import logger

from pydag.services.ui.UIAgentMgmtPage import UIAgentMgmtPage

from .UIBufferPage import UIBufferPage
from .UIElements import UIHomePage, UIPage
from ..Service import Service

@dataclass
class UIService(Service):
    """ A `Service` class that serves web ui pages based on NiceGUI.
    This class is a Singleton, meaning that only one instance of this class can exist at a time.
    This is because the NiceGUI server can only be started once, and is shared across all pages.
    The `UIService` is responsible for starting the NiceGUI server, and for managing the pages
    that are registered to it. Pages can be added to the `UIService` using the `add_page` method,
    and will be automatically registered to the NiceGUI server when it starts.
    The `UIService` also provides some default pages, such as a home page and
    a buffer visualization page, which can be enabled or disabled using the `with_buffer_ui` and
    `with_mgmt_ui` parameters. """
    
    host: str = field(default="localhost", metadata={"description": "host of the NiceGUI server"})
    port: int = field(default=8081, metadata={"description": "port of the NiceGUI server"})
    title : str = field(default="NiceGUI", metadata={"description": "dashboard title"})
    dark_mode : bool = field(default=True, metadata={"description": "enables dark mode"})
    color_schema : dict = field(default_factory=dict, metadata={"description": "color schema for the ui, see https://nicegui.io/docs/colors for more details"})
    with_buffer_ui : bool = field(default=True, metadata={"description": "creates a ui page for buffer visualization"})
    with_mgmt_ui : bool = field(default=True, metadata={"description": "creates a ui page for agent management"}) 
    
    _instance = None    # singleton instance
    _lock : threading.Lock = threading.RLock() # object lock for thread safety when creating singleton instance
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UIService, cls).__new__(cls)
        return cls._instance
    
    def __post_init__(self):
        super().__post_init__()
        self._thread : threading.Thread = None
        self._pages : list[UIPage] = []

    def _on_install(self, agent=None):
        super()._on_install(agent)
        os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
        # add home page
        self.add_page(UIHomePage(self))
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

    def get_pages(self) -> list[UIPage]:
        return self._pages

    def _run_ui_server(self):
        self._configure_app()
        self._create_pages()
        ui.run(host=self.host, port=self.port, reload=False, dark=self.dark_mode, title=self.title)
        
    def _configure_app(self):
        # define default color schema        
        if len(self.color_schema) > 0:
            app.colors(**self.color_schema)
        else:
            app.colors(
                primary='#005B95',
                secondary='#A8A8A9',
                accent='#C43726',
                positive='#00B050', 
                negative='#C43726',
            )

    def _create_pages(self):
        page : UIPage
        for page in self._pages:
            page.register()
    
