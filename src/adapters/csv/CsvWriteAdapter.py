import csv
import os
from PyDataGrabber.src.adapters.AdapterException import AdapterException
from PyDataGrabber.src.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.buffers.DictBuffer import DictBuffer
from PyDataGrabber.src.utils.FileParser import FileParser
from PyDataGrabber.src.utils.TimeParser import TimeParser


class CsvWriteAdapter(WriteAdapter):
    
    def __init__(self, id : str = None):
        super().__init__(id)
        self.folder : str = None
        self.file_post_fix : str = None
        self.file_extension : str = "csv"
        self.with_timestamp : bool = False
        self.max_samples : int = 1_000_000
        self.delimiter : str = ";"
        self.decimal_precision : int = 3
        self.csv_file = None
        self.csv_writer = None
        self.row : int = 0
        
    def connect(self) -> bool:
        if FileParser.exists_folder(self.folder):
            ts = TimeParser.utc_ms()
            file_path = self.folder.rstrip(os.path.sep) + os.path.sep + ts + "_" + self.file_post_fix + "." + self.file_extension.lstrip(".")
            self.csv_file = open(file_path, "w")
            self.csv_writer = csv.writer(self.csv_file, delimiter=self.delimiter, lineterminator="\n")
            return True
        else:
            return False
    
    def disconnect(self) -> bool:
        self.csv_writer = None
        self.csv_file.close()
        self.csv_file = None
        return True
    
    def write_to_sink(self, buffers : dict[Buffer], addresses : list[str], persistent : bool):
        if len(buffers) == 1:
            if isinstance(self, DictBuffer):
                pass
            else:
                raise AdapterException("specified buffer must be of type " + DictBuffer.__class__.__name__)            
        else:
            if addresses != None:
                pass
            else:
                pass
      
    def config_options(self) -> dict:
        d = super().config_options()
        d["folder"] = self.folder
        d["file_post_fix"] = self.file_post_fix
        d["with_timestamp"] = self.with_timestamp
        d["max_samples"] = self.max_samples
        d["delimiter"] = self.delimiter
        d["decimal_precision"] = self.decimal_precision
        return d
        