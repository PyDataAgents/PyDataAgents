from dataclasses import dataclass, field

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from loguru import logger

from ...services.ServiceException import ServiceException
from ...buffers.Buffer import Buffer
from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...services.Service import Service


@dataclass
class FileWatchdogService(Service):
    
    folders : list[str] = field(default_factory=list, metadata={"description" : "folders to watch for file events"})
    recursive : bool = field(default=True, metadata={"description" : "specifies whether to watch subdirectories as well"})
    buffer_id : str = field(default=None, metadata={"description": "Buffer ID of the buffer to store the file events into, the id specified must exist amongst buffers"})
        
    def __post_init__(self):
        super().__post_init__()
        self._observers : list[Observer] = list()
        self._file_event_buffer : DictBuffer = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self._file_event_buffer is None:
            if self.buffer_id:
                if agent:
                    buf = agent.get_buffer(self.buffer_id)
                    if buf:
                        self._file_event_buffer = buf
                        self._file_event_buffer.id = buf.id
                    else:                    
                        self._file_event_buffer = DictBuffer(id=self.buffer_id)
                        agent.add_buffer(self._file_event_buffer)
                        self._file_event_buffer.install(agent)
                else:
                    self._file_event_buffer = DictBuffer(id=self.buffer_id)
                    self._file_event_buffer.install()
            else:
                self._file_event_buffer = DictBuffer(id=f"{self.id}-Buffer")                    
                if agent:
                    agent.add_buffer(self._file_event_buffer)
                    self._file_event_buffer.install(agent)
                else:
                    self._file_event_buffer = DictBuffer(id=f"{self.id}-Buffer")
                    self._file_event_buffer.install()    
                    

    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._file_event_buffer = None
            
    def _on_start(self):
        event_handler = WatchdogHandler(self)
        for folder in self.folders:
            observer = Observer()
            observer.schedule(event_handler, path = folder, recursive = self.recursive)
            self._observers.append(observer)
            observer.start()        
        
    def _on_stop(self):
        for observer in self._observers:
            observer.stop()
            observer.join()
        

class WatchdogHandler(FileSystemEventHandler):
    
    def __init__(self, service : FileWatchdogService):
        self.service = service
    
    def on_created(self, event):
        logger.debug(f"File created: {event.src_path}")
        self.service._file_event_buffer.push(event.src_path)

    def on_modified(self, event):
        logger.debug(f"File modified: {event.dest_path}")

    def on_deleted(self, event):
        logger.debug(f"File deleted: {event.src_path}")
        self.service._file_event_buffer.push(event.src_path)
        
    def on_moved(self, event):
        logger.debug(f"File moved: {event.dest_path}")
        self.service._file_event_buffer.push(event.src_path)