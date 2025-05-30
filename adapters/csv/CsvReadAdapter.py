import csv
from dataclasses import dataclass, field
from PyDataGrabber.adapters.AdapterException import AdapterException
from PyDataGrabber.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.utils.FileUtils import FileUtils
from PyDataGrabber.buffers.DictBuffer import DictBuffer

@dataclass
class CsvReadAdapter(ReadAdapter):
    
    file_path : str = field(default=None, metadata={"description": "path to the csv file to read"})
    all_at_once : bool = field(default=True, metadata={"description": "read all data at once"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use to separate columns"})
    has_header : bool = field(default=True, metadata={"description": "specifies whether a header is present in data"})
    auto_detect : bool = field(default=False, metadata={"description": "specifies whether to use the csv sniffing option"})
    force_numeric : bool = field(default=True, metadata={"description": "forces numeric parsing of data"})
    
    def __init__(self):
        super().__init__()
        self.csv_file = None
        self.csv_reader = None
        self.headers = list()
        
    def connect(self) -> bool:
        if self.file_path != None:
            if FileUtils.exists_file(self.file_path):
                self.csv_file =  open(self.file_path, 'r')
                if self.auto_detect:
                    csv_sample = self.csv_file.read(1024)
                    dialect = csv.Sniffer().sniff(csv_sample)
                    self.has_header = csv.Sniffer().has_header(csv_sample)                    
                    self.csv_file.seek(0)
                    if self.force_numeric:
                        self.csv_reader = csv.DictReader(self.csv_file, delimiter=self.delimiter, quoting=csv.QUOTE_NONNUMERIC)    
                    else:
                        self.csv_reader = csv.DictReader(self.csv_file, delimiter=self.delimiter)
                else:
                    if self.force_numeric:
                        self.csv_reader = csv.reader(self.csv_file, delimiter=self.delimiter, quoting=csv.QUOTE_NONNUMERIC)
                    else:
                        self.csv_reader = csv.reader(self.csv_file, delimiter=self.delimiter)                
                if self.has_header:
                    # skip first row of data if header is present
                    row = next(self.csv_reader)
                return True                    
            else:
                CsvReadAdapter.LOGGER.error("File " + self.file_path + " does not exist")
                return False
        else:
            CsvReadAdapter.LOGGER.error("No File was specified") 
            return False
        
    def disconnect(self) -> bool:
        self.csv_reader = None
        self.csv_file = None
        return True
            
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1):
        if addresses != None:
            if len(buffers) != len(addresses):
                raise AdapterException("buffers and addresses must be of same size")
            if self.all_at_once:
                pass
            else:
                pass
        else:
            if len(buffers) == 1:
                buffer = buffers[buffers.keys[0]]
                if isinstance(buffer, DictBuffer):
                    if self.all_at_once:
                        for row in self.csv_reader:
                            if isinstance(row, list):
                                c = 0
                                d = {}
                                for item in list:
                                    d["COL" + c] = item
                                    c = c + 1
                                buffer.push(d)    
                            else:
                                buffer.push(row)
                    else:
                        row = next(self.csv_reader)
                        if isinstance(row, list):
                            c = 0
                            d = {}
                            for item in list:
                                d["COL" + c] = item
                                c = c + 1
                            buffer.push(d)    
                        else:
                            buffer.push(row)
                else:
                    raise AdapterException("Buffer must be of type DictBuffer")                        
    