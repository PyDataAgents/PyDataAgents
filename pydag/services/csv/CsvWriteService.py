import csv
from dataclasses import dataclass, field
import os
from loguru import logger


from ...utils.TimeUtils import TimeUtils
from ..MappingType import MappingType
from ..WriteService import WriteService
from ...utils.DataUtils import DataUtils
from ...agents.Agent import Agent
from ...buffers.Buffer import Buffer
from ...utils.FileUtils import FileUtils
from ..ServiceException import ServiceException

@dataclass
class CsvWriteService(WriteService):
    """`WriteService` for writing data to CSV files.
    """
    
    folder : str = field(default=None, metadata={"description": "folder to save the csv files to"})
    file_post_fix : str = field(default=None, metadata={"description": "postfix to use with every file"})
    file_extension : str = field(default="csv", metadata={"description": "extension of the files being created, specify without *.*, e.g. 'csv' or 'txt'"})
    max_samples : int = field(default=1_000_000, metadata={"description": "maximum number of samples in one file, if limit is reached a new file is being created"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use for column separation"})
    decimal_precision : int = field(default=3, metadata={"description": "maximum decimal precision of numeric values"})
    file_prefix_format : str = field(default=None, metadata={"description": "format of the timestamp prefix, if None then a unixtimestamp is used, otherwise formats like '%Y%m%d' can be specified"})
    
    def __post_init__(self):
        super().__post_init__()
        self._csv_file = None
        self._csv_writer = None
        self._rows : int = 0
        self.mapping_type = MappingType.WRITE.value # overwrite mapping type
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.folder is None:
            raise ServiceException("folder for " + self.__class__.__name__ + " was not specified")
        if not FileUtils.exists_folder(self.folder):
            raise ServiceException("folder " + self.folder + " does not exist")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall()
        if self._csv_file:
            self._csv_file.close()
        self._csv_file = None
        self._csv_writer = None
        self._rows = 0
    
    def write_to_sink(self):
        if len(self.get_buffers()) == 1:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            if self._rows == 0:
                data = buffer.data(n=self.n, persistent=self.persistent)
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
                data = buffer.data(n = self.n, persistent = self.persistent)                    
                # convert to row style
                data = DataUtils.dict_to_list(data)
                self._csv_writer.writerows(data)
                self._rows = self._rows + len(data)
                if self._rows > self.max_samples:
                    self._rows = 0
                    self._csv_file.close()
                    logger.debug(f"closed csv file {self._csv_file.name}")
        else:
            raise ServiceException("this combination of buffers and addresses is not implemented")
                    
    def _new_file_name(self) -> str:
        ts : str = None
        if not self.file_prefix_format is None:
            ts = TimeUtils.datetime_to_str(TimeUtils.dt_now(), self.file_prefix_format)
        else:    
            ts = str(int(TimeUtils.utc_ms()))
        
        if self.file_post_fix is None:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "." + self.file_extension.lstrip(".")
        else:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "_" + self.file_post_fix + "." + self.file_extension.lstrip(".")
        return file_path
            
        