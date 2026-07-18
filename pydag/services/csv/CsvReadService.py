import csv
from dataclasses import dataclass, field
import enum
from loguru import logger


from ...buffers.DictBuffer import DictBuffer
from ...buffers.Buffer import Buffer
from ..ServiceException import ServiceException
from ...utils.DataUtils import DataUtils
from ...agents.Agent import Agent
from ...utils.FileUtils import FileUtils
from ..MappingType import MappingType
from ..ReadService import ReadService
from ..MappingService import MappingService


class CsvReadMode(str, enum.Enum):
    ALL_AT_ONCE = "ALL_AT_ONCE"
    ONE_AT_A_TIME = "ONE_AT_A_TIME"
    LOOP = "LOOP"

@dataclass
class CsvReadService(ReadService):
    """`MappingService` for reading data from CSV files.
    """    
    
    file_path : str = field(default=None, metadata={"description": "path to the csv file to read"})
    mode : str = field(default=CsvReadMode.ONE_AT_A_TIME.value, metadata={"description": "read mode: ALL_AT_ONCE|ONE_AT_A_TIME|LOOP"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use to separate columns"})
    has_header : bool = field(default=True, metadata={"description": "specifies whether a header is present in data"})
    auto_detect : bool = field(default=False, metadata={"description": "specifies whether to use the csv sniffing option"})
    force_numeric : bool = field(default=True, metadata={"description": "forces numeric parsing of data"})
    encoding : str = field(default="utf-8", metadata={"description": "encoding of the csv file"})
    
    def __post_init__(self):
        super().__post_init__()
        self._csv_file = None
        self._csv_reader = None
        self._headers = list()
        self.mapping_type = MappingType.READ.value # overwrite mapping type
    
    def _on_install(self, agent : Agent = None):                
        super()._on_install(agent)
        if self.file_path:
            if FileUtils.exists_file(self.file_path):
                self._csv_file =  open(self.file_path, 'r', encoding=self.encoding)
                if self.auto_detect:
                    csv_sample = self._csv_file.read(1024)
                    self.has_header = csv.Sniffer().has_header(csv_sample)                    
                    self._csv_file.seek(0)
                    self._csv_reader = csv.DictReader(self._csv_file, delimiter=self.delimiter)    
                else:
                    self._csv_reader = csv.reader(self._csv_file, delimiter=self.delimiter)                
                if self.has_header and not self.auto_detect:
                    # skip first row of data if header is present
                    row = next(self._csv_reader, None)
            else:
                raise ServiceException("File " + self.file_path + " does not exist")
        else:
            raise ServiceException("No File was specified")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._csv_reader = None
        self._csv_file = None
            
    def read_from_source(self):
        if len(self.get_buffers()) > 1 and len(self.get_buffers()) != len(self.addresses):
            raise ServiceException(Buffer.__name__+ "s and addresses must be of same size")
        elif len(self.get_buffers()) == 1 and len(self.addresses) == 0:
            buffer = next(iter(self.get_buffers().values()))
            if isinstance(buffer, DictBuffer):
                match self.mode:
                    case CsvReadMode.ALL_AT_ONCE.value:
                        for row in self._csv_reader:
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
                    case CsvReadMode.ONE_AT_A_TIME.value:
                        row = next(self._csv_reader, None)
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
                            logger.warning("end of file " + self.file_path + " was reached, no more data will be added")
                        else:
                            if self.force_numeric:
                                converted_row = {k: DataUtils.force_numeric(v) for k, v in row.items()}
                                buffer.push(converted_row)
                            else:    
                                buffer.push(row)
                    
                    case CsvReadMode.LOOP.value:
                        row = next(self._csv_reader, None)
                        if row is None:
                            # restart the file and re-create the reader
                            self._csv_file.seek(0)
                            if self.auto_detect:
                                self._csv_reader = csv.DictReader(self._csv_file, delimiter=self.delimiter)
                            else:
                                self._csv_reader = csv.reader(self._csv_file, delimiter=self.delimiter)
                                if self.has_header:
                                    # skip first row of data if header is present
                                    _ = next(self._csv_reader, None)
                            row = next(self._csv_reader, None)
                        if isinstance(row, list):
                            c = 0
                            d = {}
                            if self.force_numeric:
                                for item in row:
                                    d["COL" + str(c)] = DataUtils.force_numeric(item)
                                    c = c + 1
                            else:
                                for item in row:
                                    d["COL" + str(c)] = item
                                    c = c + 1
                            buffer.push(d)
                        else:
                            if self.force_numeric:
                                converted_row = {k: DataUtils.force_numeric(v) for k, v in row.items()}
                                buffer.push(converted_row)
                            else:
                                buffer.push(row)
            else:
                raise ServiceException(Buffer.cname() + " must be of type " + DictBuffer.cname())
        else:
            raise ServiceException("combination of buffers and addresses is not implemented")