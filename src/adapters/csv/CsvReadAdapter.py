import csv
from PyDataGrabber.src.adapters.AdapterException import AdapterException
from PyDataGrabber.src.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.utils.FileParser import FileParser
from PyDataGrabber.src.buffers.DictBuffer import DictBuffer

class CsvReadAdapter(ReadAdapter):
    
    def __init__(self, id):
        super().__init__(id)
        self.file_path = None
        self.all_at_once = False
        self.delimiter = ";"
        self.has_header = True
        self.auto_detect = False
        self.force_numeric = True
        self.csv_file = None
        self.csv_reader = None
        self.headers = list()
        
    def connect(self) -> bool:
        if self.file_path != None:
            if FileParser.exists_file(self.file_path):
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
        
    def config_options(self) -> dict:
        d = super().config_options()
        d["file_path"] = self.file_path
        d["all_at_once"] = self.all_at_once
        d["delimiter"] = self.delimiter
        d["force_numeric"] = self.force_numeric
        d["has_header"] = self.has_header
        return d
    
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
    