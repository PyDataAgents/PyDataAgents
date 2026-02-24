import csv
from dataclasses import dataclass, field

from ...buffers.DictBuffer import DictBuffer

from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class ReadCsvAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the csv file to read the data from"})
    delimiter : str = field(default=";", metadata={"description" : "delimiter character(s) for this csv file"})
    
    def _on_execute(self):
        with open(self.file_path, 'r', encoding='utf-8') as csv_file:
            csv_sample = csv_file.read(1024)
            dialect = csv.Sniffer().sniff(csv_sample)
            has_header = csv.Sniffer().has_header(csv_sample)                    
            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file, delimiter=self.delimiter)    
            if isinstance(self._buffer, DictBuffer):
                for row in csv_reader:
                    if isinstance(row, list):
                        c = 0
                        d = {}
                        for item in list:
                            d["COL" + c] = self.__try_numeric(item)
                            c = c + 1
                        self.add_data(d)    
                    else:
                        converted_row = {key: self.__try_numeric(value) for key, value in row.items()}
                        self.add_data(converted_row)
                        
        
    def __try_numeric(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value  # Keep as string if not numeric
    