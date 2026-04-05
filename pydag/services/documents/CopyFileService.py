from dataclasses import dataclass, field
import os


from ...agents.Agent import Agent
from ...utils.TimeUtils import TimeUtils
from ...utils.FileUtils import FileUtils
from ..Observer import Observer
from ...services.ThreadType import ThreadType
from ...services.ObserverService import ObserverService


@dataclass
class CopyFileService(ObserverService):
    """
    `Service`to copy files from one location to another
    """
    
    source_folders : list[str] = field(default_factory=list, metadata={"description": "List of source folders to copy files from."})
    target_folder : str = field(default=None, metadata={"description": "Target folder where files will be copied to."})
    move : bool = field(default=False, metadata={"description": "If True, files will be moved instead of copied."})
    older_than_milliseconds : int = field(default=None, metadata={"description": "If set, only files older than this time will be copied or moved."})
    thread_type : str = field(default=ThreadType.SECOND.value, metadata={"description": "second precision observerthread"})
    observing_time : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check for new files."})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        observer = CopyFileObserver(self)
        self._observer_thread.add_observer(observer)        
     
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
        return