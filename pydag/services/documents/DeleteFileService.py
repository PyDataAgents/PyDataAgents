from dataclasses import dataclass, field


from ...agents import Agent
from ...utils.TimeUtils import TimeUtils
from ...utils.FileUtils import FileUtils
from ..Observer import Observer
from ...services.ThreadType import ThreadType
from ...services.ObserverService import ObserverService


@dataclass
class DeleteFileService(ObserverService):
    """
    `Service` to delete files from folders
    """
    
    folders : list[str] = field(default_factory=list, metadata={"description": "List of folders to delete files from."})
    older_than_milliseconds : int = field(default=None, metadata={"description": "If set, only files older than this time will be deleted."})
    thread_type : str = field(default=ThreadType.SECOND.value, metadata={"description": "second precision observerthread"})
    observing_time : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check for new files."})
            
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # Create a thread to periodically check for new files
        observer = DeleteFileObserver(self)
        self.add_observer(observer)
    
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
        return