import csv
from dataclasses import dataclass, field
import os
from loguru import logger

from pydag.utils.DataUtils import DataUtils


from ...agents.Agent import Agent
from ...adapters.AdapterException import AdapterException
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer
from ...utils.FileUtils import FileUtils
from ...utils.TimeUtils import TimeUtils

@dataclass
class CsvWriteAdapter(WriteAdapter):
    """`Adapter` for writing data to CSV files.
    """
    
    folder : str = field(default=None, metadata={"description": "folder to save the csv files to"})
    file_post_fix : str = field(default=None, metadata={"description": "postfix to use with every file"})
    file_extension : str = field(default="csv", metadata={"description": "extension of the files being created, specify without *.*, e.g. 'csv' or 'txt'"})
    max_samples : int = field(default=1_000_000, metadata={"description": "maximum number of samples in one file, if limit is reached a new file is being created"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use for column separation"})
    decimal_precision : int = field(default=3, metadata={"description": "maximum decimal precision of numeric values"})
    
    def __post_init__(self):
        super().__post_init__()
        self._csv_file = None
        self._csv_writer = None
        self._rows : int = 0
        
    def _on_install(self, agent : Agent = None):
        return
        
    def _on_uninstall(self, agent : Agent = None):
        self._csv_file = None
        self._csv_writer = None
        self._rows = 0
            
    def _on_connect(self) -> bool:
        if self.folder is None:
            logger.error("folder for " + self.cname() + " was not specified")
            return False
        if FileUtils.exists_folder(self.folder):
            return True
        else:
            return False
    
    def _on_disconnect(self) -> bool:
        if self._csv_file:
            self._csv_file.close()
        return True
    
    def _on_write(self, buffers : dict[Buffer], addresses : list[str], n : int = 1, persistent : bool = False):
        if len(buffers) == 1:
            buffer : Buffer = next(iter(buffers.values()))
            if self._rows == 0:
                data = buffer.data(n=1, persistent=True)
                if data is None:
                    logger.debug("no data available in buffer " + buffer.cname() + " to write to csv")
                    return 
                headers = list()
                headers = data.keys()
                # convert to row style
                data = DataUtils.dict_to_list(data)
                
                self._csv_file = open(self._new_file_name(), "w", encoding="utf-8")
                self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=headers, delimiter=self.delimiter, lineterminator="\n")            
                self._csv_writer.writeheader()
                self._csv_writer.writerows(data)
                self._rows = self._rows + len(data)
            else:
                if n == 1:
                    data = buffer.data(n = n, persistent = persistent)                    
                    # convert to row style
                    data = DataUtils.dict_to_list(data)
                    self._csv_writer.writerows(data)
                    self._rows = self._rows + len(data)
                    if self._rows > self.max_samples:
                        self._rows = 0
                        self._csv_file.close()
                        logger.debug("closed csv file in " + self.folder)
                else:
                    raise AdapterException("write_to_sink is not defined for n > 1")
        else:
            raise AdapterException("this combination of buffers and addresses is not implemented")
                    
    def _new_file_name(self) -> str:
        ts = str(int(TimeUtils.utc_ms()))
        if self.file_post_fix is None:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "." + self.file_extension.lstrip(".")
        else:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "_" + self.file_post_fix + "." + self.file_extension.lstrip(".")
        return file_path
            
        