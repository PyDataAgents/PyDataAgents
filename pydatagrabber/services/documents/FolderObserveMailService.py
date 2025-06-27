from dataclasses import dataclass, field
from datetime import datetime

from pydatagrabber.utils.FileUtils import FileUtils

from ...utils.TimeUtils import TimeUtils
from ...mappings.Observer import Observer
from ...mappings.ThreadType import ThreadType
from ...mappings.ObserverThread import ObserverThread
from ...services.Service import Service
from ...buffers.DictBuffer import DictBuffer
from ...grabbers.Grabber import Grabber
from ...statemachine.actions.MailAction import MailAction


@dataclass
class FolderObserveMailService(Service):
    """
    `Service` to observe a folder for new files and alert by mail on events.
    """
    
    folder : str = field(default=None, metadata={"description": "Path to the folder to observe."})
    interval : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check the folder for new files."})
    skip_weekends : bool = field(default=True, metadata={"description": "If True, the service will not check for new files on weekends."})
    max_entries : int = field(default=5, metadata={"description": "Maximum number of entries to keep as history."})
    list_files : bool = field(default=True, metadata={"description": "If True, the service will list files in the mail body."})
    html_report : bool = field(default=True, metadata={"description": "If True, the mail will be sent as HTML."})
    mail_action : MailAction = field(default_factory=None, metadata={"description": "MailAction object to send a mail with file infos."})

    # Constants for the mail content
    COL_DATE : str = "Datetime"
    COL_NUM_FILES : str = "Number of Files"
    COL_FOLDER_SIZE : str = "Folder Size [MB]"
    COL_FILE_EXTENSIONS : str = "File Extensions"
    COL_FILENAME : str = "Filename"
    COL_LINK : str = "Link"
        
    def __init__(self):
        super().__init__()
        self.file_history_buffer : DictBuffer = None
        self.service_thread : ObserverThread = None
        
    def install(self, grabber : Grabber = None):
        super().install()
        # instatiate buffer for file history
        self.file_history_buffer = DictBuffer()
        self.file_history_buffer.id = self.id + " - FILE HISTORY",
        self.file_history_buffer.capacity = self.max_entries,
        self.file_history_buffer.description = "Buffer to keep track of file history in the observed folder."        

    def start(self):
        super().start()
        # create new thread for update interval of folder observation
        self.service_thread = ObserverThread(self.unique_id() + "-Thread", ThreadType.MILLI_SECOND, self.interval * 1000)
        observer = FolderMailObserver(self)
        self.service_thread.add_observer(observer)     

    def stop(self):
        pass
    
class FolderMailObserver(Observer):
    """
    Observer to handle the folder observation events.
    """
    
    def __init__(self, folderObserveMailService: FolderObserveMailService):
        super().__init__()
        self.service = folderObserveMailService
            
    def observe(self):
        # Logic to check the folder for new files and send mail if necessary
        if self.service.skip_weekends:
            # Check if today is a weekend and skip if so
            if datetime.now().weekday() >= 5:
                return
        
        ts : str = TimeUtils.now_iso8601()
        files = FileUtils.list_files(self.service.folder)
        if len(files) == 0:
            self.LOGGER.warning(f"No files found in folder {self.service.folder} at {ts}.")
            return

        nf = len(files)
        fb = FileUtils.get_folder_bytes(self.service.folder) / (1024 * 1024)  # Convert to MB
        file_extensions = FileUtils.get_extensions_from_folder(self.service.folder)
        
        row_data = {
            self.service.COL_DATE: ts,
            self.service.COL_NUM_FILES: nf,
            self.service.COL_FOLDER_SIZE: fb,
            self.service.COL_FILE_EXTENSIONS: ", ".join(file_extensions),
        }
        
        self.service.file_history_buffer.push(row_data)
        
        # create html table from dictbuffer
        # TODO
        
    
    def unobserve(self):
        pass
    