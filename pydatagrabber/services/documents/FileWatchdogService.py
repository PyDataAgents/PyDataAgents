from dataclasses import dataclass, field

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ...services.ServiceException import ServiceException
from ...buffers.Buffer import Buffer
from ...grabbers.Grabber import Grabber
from ...buffers.DictBuffer import DictBuffer
from ...services.Service import Service


@dataclass
class FileWatchdogService(Service):
    
    folders : list[str] = field(default_factory=list, metadata={"description" : "folders to watch for file events"})
    recursive : bool = field(default=True, metadata={"description" : "specifies whether to watch subdirectories as well"})
    buffer_id : str = field(default=None, metadata={"description": "Buffer ID of the buffer to store the file events into, the id specified must exist amongst buffers"})
        
    def __init__(self):
        super().__init__()
        self.observers : list[Observer] = list()
        self.file_event_buffer : DictBuffer = None
    
    def install(self, grabber : Grabber):
        self.install(grabber)
        if self.file_event_buffer is None:
            if self.buffer_id in grabber.buffer_store:
                self.file_event_buffer = grabber.buffer_store[self.buffer_id]
            else:
                raise ServiceException("No " + Buffer.cname() + " with id=" + self.buffer_id + " exists in " + Grabber.cname())

    def deinstall(self, grabber : Grabber):
        super().deinstall(grabber)
        self.file_event_buffer = None
            
    def start(self):
        super().start()
        event_handler = WatchdogHandler(self)
        for folder in self.folders:
            observer = Observer()
            observer.schedule(event_handler, path = folder, recursive = self.recursive)
            self.observers.append(observer)
            observer.start()        
        
    def stop(self):
        super().stop()
        for observer in self.observers:
            observer.stop()
            observer.join()
        

class WatchdogHandler(FileSystemEventHandler):
    
    def __init__(self, service : FileWatchdogService):
        self.service = service
    
    def on_created(self, event):
        self.service.LOGGER.debug(f"File created: {event.src_path}")
        self.service.file_event_buffer.push(event.src_path)

    def on_modified(self, event):
        self.service.LOGGER.debug(f"File modified: {event.dest_path}")

    def on_deleted(self, event):
        self.service.LOGGER.debug(f"File deleted: {event.src_path}")
        self.service.file_event_buffer.push(event.src_path)
        
    def on_moved(self, event):
        self.service.LOGGER.debug(f"File moved: {event.dest_path}")
        self.service.file_event_buffer.push(event.src_path)