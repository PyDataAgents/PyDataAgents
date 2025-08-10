import csv
from dataclasses import dataclass, field
import enum
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...buffers.Buffer import Buffer
from ...utils.FileUtils import FileUtils
from ...buffers.DictBuffer import DictBuffer
from ...utils.DataUtils import DataUtils

class CSVReadMode(str, enum.Enum):
    ALL_AT_ONCE = "ALL_AT_ONCE"
    ONE_AT_A_TIME = "ONE_AT_A_TIME"
    LOOP = "LOOP"

@dataclass
class CsvReadAdapter(ReadAdapter):
    """`Adapter` for reading data from CSV files.
    """
    
    file_path : str = field(default=None, metadata={"description": "path to the csv file to read"})
    mode : str = field(default=CSVReadMode.ONE_AT_A_TIME.value, metadata={"description": "read mode: ALL_AT_ONCE|ONE_AT_A_TIME|LOOP"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use to separate columns"})
    has_header : bool = field(default=True, metadata={"description": "specifies whether a header is present in data"})
    auto_detect : bool = field(default=False, metadata={"description": "specifies whether to use the csv sniffing option"})
    force_numeric : bool = field(default=True, metadata={"description": "forces numeric parsing of data"})
    
    def __post_init__(self):
        super().__post_init__()
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
                    self.csv_reader = csv.DictReader(self.csv_file, delimiter=self.delimiter)    
                else:
                    self.csv_reader = csv.reader(self.csv_file, delimiter=self.delimiter)                
                if self.has_header and not self.auto_detect:
                    # skip first row of data if header is present
                    row = next(self.csv_reader, None)
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
        if len(buffers) > 1 and len(buffers) != len(addresses):
            raise AdapterException(Buffer.cname() + "s and addresses must be of same size")            
        elif len(buffers) == 1 and len(addresses) == 0:
            buffer = next(iter(buffers.values()))
            if isinstance(buffer, DictBuffer):
                match self.mode:
                    case CSVReadMode.ALL_AT_ONCE.value:
                        for row in self.csv_reader:
                            if isinstance(row, list):
                                c = 0
                                d = {}
                                if self.force_numeric:
                                    for item in list:
                                        d["COL" + c] = DataUtils.force_numeric(item)                                        
                                        c = c + 1
                                else:
                                    for item in list:
                                        d["COL" + c] = item                                     
                                        c = c + 1
                                buffer.push(d)    
                            else:
                                if self.force_numeric:
                                    converted_row = {key: DataUtils.force_numeric(value) for key, value in row.items()}
                                    buffer.push(converted_row)
                                else:
                                    buffer.push(row)
                    case CSVReadMode.ONE_AT_A_TIME.value:
                        row = next(self.csv_reader, None)
                        if isinstance(row, list):
                            c = 0
                            d = {}
                            if self.force_numeric:
                                for item in list:
                                    d["COL" + c] = DataUtils.force_numeric(item) 
                                    c = c + 1
                            else:
                                for item in list:
                                    d["COL" + c] = item
                                    c = c + 1
                            buffer.push(d)    
                        elif row is None:
                            self.LOGGER.warning("end of file " + self.file_path + " was reached, no more data will be added")
                        else:
                            if self.force_numeric:
                                converted_row = {k: DataUtils.force_numeric(v) for k, v in row.items()}
                                buffer.push(converted_row)
                            else:    
                                buffer.push(row)
                    
                    case CSVReadMode.LOOP.value:
                        row = next(self.csv_reader, None)
                        if row is None:
                            self.csv_file.seek(0)
                            if self.auto_detect:
                                self.csv_reader = csv.DictReader(self.csv_file, delimiter=self.delimiter) 
                            else:
                                self.csv_reader = csv.reader(self.csv_file, delimiter=self.delimiter)                
                                if self.has_header:
                                    # skip first row of data if header is present
                                    row = next(self.csv_reader, None)
                            row = next(self.csv_reader, None)
                        if isinstance(row, list):
                            c = 0
                            d = {}
                            if self.force_numeric:
                                for item in list:
                                    d["COL" + c] = DataUtils.force_numeric(item) 
                                    c = c + 1
                            else:
                                for item in list:
                                    d["COL" + c] = item
                                    c = c + 1
                            buffer.push(d)    
                        else:
                            if self.force_numeric:
                                converted_row = {k: DataUtils.force_numeric(v) for k, v in row.items()}
                                buffer.push(converted_row)
                            else:    
                                buffer.push(row)
            else:
                raise AdapterException(Buffer.cname() + " must be of type " + DictBuffer.cname())
        else:
            raise AdapterException("combination of buffers and addresses is not implemented")