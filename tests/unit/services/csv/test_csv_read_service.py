import csv
import os
import time
from pydag.buffers.Buffer import Buffer
from pydag.buffers.DataType import DataType
from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.csv.CsvReadService import CsvReadService, CsvReadMode

def test_000():
    script_path = os.getcwd()
    print(script_path)
    print(os.path.dirname(__file__))
    with open(os.path.dirname(__file__) + '\\data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test_001():
    with open(os.path.dirname(__file__) + '\\data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test_002():
    csv_file =  open(os.path.dirname(__file__) + '\\data.csv', 'r', encoding='utf-8')
    csv_sample = csv_file.read(1024)
    has_header = csv.Sniffer().has_header(csv_sample)
    print(has_header)                    
    csv_file.seek(0)
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    

def test_010():
    csv_adapter = CsvReadService()
    csv_adapter.id = "CSV1"
    csv_adapter.mode = CsvReadMode.LOOP.value
    print(csv_adapter.config_options())
    

def test_020():
    
    buf1 = DictBuffer(id = "BSD_DATA", capacity = 500, data_type = DataType.FLOAT.value, description = "ball screw drive data")
    buf1.install()
    
    a1 = CsvReadService(id = "CSV1",
                        mode = CsvReadMode.LOOP.value,
                        auto_detect = True,
                        file_path = os.path.dirname(__file__) + os.sep + "ballscrew_drive_data.csv",
                        force_numeric = True,
                        thread_type=ThreadType.MILLI_SECOND.value,
                        mapping_type=MappingType.READ.value)
    a1.add_buffer(buf1)
    i = 0
    i_max = 100
    
    a1.install()
    while i < i_max:    
        a1._read_from_source()
        print(buf1.data())
        time.sleep(0.05)
        i = i + 1       

def test_021():
    
    buf1 = DictBuffer(id = "TESTDATA", capacity = 500, data_type = DataType.FLOAT.value, description = "test data")
    buf1.install()
    
    a1 = CsvReadService(id = "CSV1",
                        mode = CsvReadMode.LOOP.value,
                        auto_detect = True,
                        file_path = os.path.dirname(__file__) + os.sep + "data2.csv",
                        force_numeric = True,
                        thread_type=ThreadType.MILLI_SECOND.value,
                        mapping_type=MappingType.READ.value)
    a1.add_buffer(buf1)
    i = 0
    i_max = 5
    
    a1.install()
    while i < i_max:    
        a1._read_from_source()
        print(buf1.data())
        time.sleep(0.5)
        i = i + 1
        
        
def test_030():
    
    a1 = CsvReadService(has_header=False)    
    print(a1.config_options())