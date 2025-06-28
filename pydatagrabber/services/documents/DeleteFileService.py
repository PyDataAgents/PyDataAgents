from dataclasses import dataclass, field
import os

from ...utils.TimeUtils import TimeUtils
from ...utils.FileUtils import FileUtils
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ...services.Service import Service


@dataclass
class DeleteFileService(Service):
    """
    `Service` to delete files from folders
    """
    
    folders : list[str] = field(default_factory=list, metadata={"description": "List of folders to delete files from."})
    older_than_milliseconds : int = field(default=None, metadata={"description": "If set, only files older than this time will be deleted."})
    interval : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check for new files."})
    
    def __init__(self):
        super().__init__()
        self.service_thread = None
        
    def start(self):
        super().start()
        # Create a thread to periodically check for new files
        self.service_thread = ObserverThread(self.unique_id() + "-Thread", ThreadType.MILLI_SECOND, self.interval * 1000)
        observer = DeleteFileObserver(self)
        self.service_thread.add_observer(observer)
        self.service_thread.start()
    
    def stop(self):
        self.service_thread.stop()
        super().stop()

class DeleteFileObserver(Observer):
    
    def __init__(self, service: DeleteFileService):
        self.service = service

    def observe(self):
        for folder in self.service.folders:
            files = FileUtils.list_files(folder)
            for file in files:
                if self.service.older_than_milliseconds is not None:
                    file_age = FileUtils.get_modified_date_ms(file)
                    if TimeUtils.utc_ms() - file_age > self.service.older_than_milliseconds:
                        FileUtils.delete_file(file)                        
                else:
                    FileUtils.delete_file(file)
    
    def unobserve(self):
        pass