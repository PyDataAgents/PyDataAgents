from dataclasses import dataclass, field

from ...buffers.DictBuffer import DictBuffer
from ...grabbers.Grabber import Grabber
from ...statemachine.actions.MailAction import MailAction


@dataclass
class FolderObserveMailService:
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
        file_history_buffer : DictBuffer = None
        
    def install(self, grabber : Grabber = None):
        # TODO instatiate buffer for file history
        pass

    def start(self):
        pass
        

    def stop(self):
        pass

    