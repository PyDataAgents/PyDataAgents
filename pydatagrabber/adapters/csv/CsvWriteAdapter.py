import csv
from dataclasses import dataclass, field
import os
from ...adapters.AdapterException import AdapterException
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ...utils.TimeUtils import TimeUtils

@dataclass
class CsvWriteAdapter(WriteAdapter):
    """`Adapter` for writing data to CSV files.
    """
    
    folder : str = field(default=None, metadata={"description": "folder to save the csv files to"})
    file_post_fix : str = field(default=None, metadata={"description": "postfix to use with every file"})
    file_extension : str = field(default="csv", metadata={"description": "extension of the files being created, specify without *.*, e.g. 'csv' or 'txt'"})
    with_timestamp : bool = field(default=False, metadata={"description": "specify whether the current timestamp in UTC ms should be printed as column"})
    max_samples : int = field(default=1_000_000, metadata={"description": "maximum number of samples in one file, if limit is reached a new file is being created"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use for column separation"})
    decimal_precision : int = field(default=3, metadata={"description": "maximum decimal precision of numeric values"})
    
    def __init__(self):
        super().__init__()
        self.csv_file = None
        self.csv_writer = None
        self.rows : int = 0
        
    def connect(self) -> bool:
        if FileUtils.exists_folder(self.folder):
            self.csv_file = open(self._new_file_name(), "w")
            self.csv_writer = csv.writer(self.csv_file, delimiter=self.delimiter, lineterminator="\n")
            return True
        else:
            return False
    
    def disconnect(self) -> bool:
        self.csv_writer = None
        self.csv_file.close()
        self.csv_file = None
        return True
    
    def write_to_sink(self, buffers : dict[Buffer], addresses : list[str], n : int = 1, persistent : bool = False):
        if len(buffers) == 1:
            if isinstance(self, DictBuffer):
                buffer : DictBuffer = buffers[buffers.key()[0]]
                if self.rows == 0:
                    if self.with_timestamp:
                        headers = list()
                        headers.append("TIMESTAMP [ms]")
                        headers.extend(buffer.elements.keys())
                    else:
                        headers = buffer.elements.keys()
                    self.csv_writer.writerow(headers)
                    self.rows = self.rows + 1
                else:
                    if n == 1:
                        d = dict()
                        d["TIMESTAMP [ms]"] = TimeUtils.utc_ms()
                        d.update(buffer.data(n = n, persistent = persistent))
                        self.csv_writer.writerow(d)
                        self.rows = self.rows + 1
                        if self.rows > self.max_samples:
                            self.rows = 0
                            self.csv_file.close()
                            self.csv_file = open(self._new_file_name(), "w")
                            self.csv_writer = csv.writer(self.csv_file, delimiter=self.delimiter, lineterminator="\n")
                            self.LOGGER.debug("created new csv file in " + self.folder)
                    else:
                        raise AdapterException("write_to_sink is not defined for n > 1")
            else:
                raise AdapterException("specified buffer must be of type " + DictBuffer.__class__.__name__)            
        else:
            if addresses != None:
                pass
            else:
                if self.rows == 0:
                    if self.with_timestamp:
                        headers = list()
                        headers.append("TIMESTAMP [ms]")
                        headers.extend(buffers.keys())
                    else:
                        headers = buffers.keys()
                    self.csv_writer.writerow(headers)
                    self.rows = self.rows + 1
                else:
                    if n == 1:
                        d = list()
                        if self.with_timestamp:
                            d.append(TimeUtils.utc_ms())
                        for key in buffers.keys():                        
                            d.append(buffers[key].data(n = n, persistent = persistent))
                        self.csv_writer.writerow(d)
                        self.rows = self.rows + 1
                        if self.rows > self.max_samples:
                            self.rows = 0
                            self.csv_file.close()
                            self.csv_file = open(self._new_file_name(), "w")
                            self.csv_writer = csv.writer(self.csv_file, delimiter=self.delimiter, lineterminator="\n")
                            self.LOGGER.debug("created new csv file in " + self.folder)
                    else:
                        raise AdapterException("write_to_sink is not defined for n > 1") 
                    
    def _new_file_name(self) -> str:
        ts = TimeUtils.utc_ms()
        if self.file_post_fix is None:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "." + self.file_extension.lstrip(".")
        else:
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "_" + self.file_post_fix + "." + self.file_extension.lstrip(".")
        return file_path
            
        