from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from loguru import logger

from ...utils.HTMLUtils import HTMLUtils
from ...utils.FileUtils import FileUtils
from ...utils.TimeUtils import TimeUtils
from ..Observer import Observer
from ...services.ThreadType import ThreadType
from ...services.ObserverService import ObserverService
from ...buffers.DictBuffer import DictBuffer
from ...agents.Agent import Agent
from ...nodes.utils.MailAction import MailAction


# Constants for the mail content
COL_DATE : str = "Datetime"
COL_NUM_FILES : str = "Number of Files"
COL_FOLDER_SIZE : str = "Folder Size [MB]"
COL_FILE_EXTENSIONS : str = "File Extensions"
COL_FILENAME : str = "Filename"
COL_LINK : str = "Link"

MAX_FILES : int = 50  # Maximum number of files to list in the mail body
    
@dataclass
class FolderObserveMailService(ObserverService):
    """
    `Service` to observe a folder for new files and alert by mail on events.
    """
    
    thread_type : str = field(default=ThreadType.SECOND.value, metadata={"description": "second precision observerthread"})
    observing_time : int = field(default=60*60*24, metadata={"description": "Interval in seconds to check for new files."})    
    folder : str = field(default=None, metadata={"description": "Path to the folder to observe."})
    skip_weekends : bool = field(default=True, metadata={"description": "If True, the service will not check for new files on weekends."})
    max_entries : int = field(default=5, metadata={"description": "Maximum number of entries to keep as history."})
    list_files : bool = field(default=True, metadata={"description": "If True, the service will list files in the mail body."})
    html_report : bool = field(default=True, metadata={"description": "If True, the mail will be sent as HTML."})
    mail_action : MailAction = field(default_factory=MailAction, metadata={"description": "MailAction object to send a mail with file infos."})
    skip_extensions : list[str] = field(default_factory=list[str], metadata={"description": "specifies the file extensions that should be ignored in listing"})
        
    def __post_init__(self):
        super().__post_init__()
        self._file_history_buffer : DictBuffer = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # instatiate buffer for file history
        self._file_history_buffer = DictBuffer()
        self._file_history_buffer.id = self.id + " - FILE HISTORY"
        self._file_history_buffer.capacity = self.max_entries
        self._file_history_buffer.description = "Buffer to keep track of file history in the observed folder."# create new thread for update interval of folder observation
        observer = FolderMailObserver(self)
        self.add_observer(observer)
    
    def get_file_history(self) -> DictBuffer:
        return self._file_history_buffer
            
class FolderMailObserver(Observer):
    """
    Observer to handle the folder observation events.
    """
    
    def __init__(self, service : FolderObserveMailService):
        super().__init__()
        self._service = service
            
    def observe(self):
        # Logic to check the folder for new files and send mail if necessary
        if self._service.skip_weekends:
            # Check if today is a weekend and skip if so
            if datetime.now().weekday() >= 5:
                return
        
        ts : str = TimeUtils.now_iso8601()
        files = FileUtils.list_files(self._service.folder)
        # filter for skip_extension
        if len(self._service.skip_extensions):
            files = [
                path for path in files 
                if Path(path).suffix.lower() not in self._service.skip_extensions
            ]

        if len(files) == 0:
            logger.warning(f"No files found in folder {self._service.folder} at {ts}.")
            return

        nf = len(files)
        fb = round(FileUtils.get_folder_bytes(self._service.folder) / (1024 * 1024),2)  # Convert to MB
        file_extensions = FileUtils.get_extensions_from_folder(self._service.folder)
        
        row_data = {
            COL_DATE: ts,
            COL_NUM_FILES: nf,
            COL_FOLDER_SIZE: fb,
            COL_FILE_EXTENSIONS: ", ".join(file_extensions),
        }
        
        self._service.get_file_history().push(row_data)
        
        # create html table from dictbuffer
        html_table = HTMLUtils.dict_to_htmltable(self._service.get_file_history().data())
        body = "<h4>" + FolderObserveMailService.cname() + " - " + self._service.folder + "</h4>\n" + html_table
        
        # add file infos to body
        if self._service.list_files:
            body += "\n<hr><h4>Files:</h4>"
            file_buf = DictBuffer()
            file_buf.capacity = MAX_FILES
            for f in files:
                file_row = {
                    COL_FILENAME: FileUtils.file_name(f),
                    COL_LINK: f"<a href='file://{f}'>{f}</a>"
                }
                file_buf.push(file_row)
            
            html_table = HTMLUtils.dict_to_htmltable(file_buf.data())            
            body += html_table
            if len(files) > MAX_FILES:
                body += f"Note: Only the last {MAX_FILES} files are listed."
        
        # send mail
        if self._service.mail_action.subject is None:
            self._service.mail_action.subject = FolderObserveMailService.cname() + " for " + self._service.folder + " - Do Not Reply"
        self._service.mail_action.body = body
        self._service.mail_action.execute()
    
    def unobserve(self):
        return
    