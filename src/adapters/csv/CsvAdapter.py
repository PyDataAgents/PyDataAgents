import csv
from PyDataGrabber.src.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.src.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.src.utils.FileParser import FileParser


class CsvAdapter(ReadAdapter, WriteAdapter):
    
    def __init__(self, id):
        super().__init__(id)
        self.file_path = None
        self.all_at_once = False
        self.delimiter = ";"
        self.csv_file = None
        self.csv_reader = None
        
    def file_path(self, file_path : str):
        self.file_path = file_path
        return self
    
    def all_at_once(self, all_at_once : str):
        self.all_at_once = all_at_once
        return self
    
    def delimiter(self, delimiter : str):
        self.delimiter = delimiter
        return self
        
    def connect(self) -> bool:
        if self.file_path != None:
            if FileParser.exists_file(self.file_path):
                self.csv_file =  open(self.file_path, 'r')
                self.csv_reader = csv.reader(self.csv_file)
            else:
                return False
        else: 
            return False
        
    def config_options(self) -> dict:
        d = super().config_options()
        d["file_path"] = self.file_path
        d["all_at_once"] = self.all_at_once
        d["delimiter"] = self.delimiter
        return d
    
    def readFromSource(buffers : dict, addresses : list):
        
        pass
    
    def writeToSink(buffers : dict, addresses : list, persistent : bool):
        pass
        
    