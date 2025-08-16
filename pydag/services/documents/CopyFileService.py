from dataclasses import dataclass, field
import os
from loguru import logger

from ...utils.TimeUtils import TimeUtils
from ...utils.FileUtils import FileUtils
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ...services.Service import Service


@dataclass
class CopyFileService(Service):
    """
    `Service`to copy files from one location to another
    """
    
    source_folders : list[str] = field(default_factory=list, metadata={"description": "List of source folders to copy files from."})
    target_folder : str = field(default=None, metadata={"description": "Target folder where files will be copied to."})
    move : bool = field(default=False, metadata={"description": "If True, files will be moved instead of copied."})
    older_than_milliseconds : int = field(default=None, metadata={"description": "If set, only files older than this time will be copied or moved."})
    interval : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check for new files."})
    
    def __post_init__(self):
        super().__post_init__()
        self.service_thread = None
        
    def start(self):
        super().start()
        # Create a thread to periodically check for new files
        self.service_thread = ObserverThread(self.unique_id() + "-Thread", ThreadType.MILLI_SECOND, self.interval * 1000)
        observer = CopyFileObserver(self)
        self.service_thread.add_observer(observer)
        self.service_thread.start()
    
    def stop(self):
        self.service_thread.stop()
        super().stop()

class CopyFileObserver(Observer):
    
    def __init__(self, service: CopyFileService):
        self.service = service

    def observe(self):
        for source_folder in self.service.source_folders:
            files = FileUtils.list_files(source_folder)
            for file in files:
                if self.service.older_than_milliseconds is not None:
                    file_age = FileUtils.get_modified_date_ms(file)
                    if TimeUtils.utc_ms() - file_age > self.service.older_than_milliseconds:
                        target_file = os.path.join(self.service.target_folder, os.path.basename(file))
                        if self.service.move:
                            FileUtils.move_file(file, target_file)
                        else:
                            FileUtils.copy_file(file, target_file)
                else:
                    target_file = os.path.join(self.service.target_folder, os.path.basename(file))
                    if self.service.move:
                        FileUtils.move_file(file, target_file)
                    else:
                        FileUtils.copy_file(file, target_file)
    
    def unobserve(self):
        pass