import csv
import os
import time
from pydg.adapters.csv.CsvReadAdapter import CsvReadAdapter
from pydg.buffers.Buffer import Buffer
from pydg.buffers.DataType import DataType
from pydg.buffers.DictBuffer import DictBuffer
from pydg.utils.BufferUtils import BufferUtils

def test_000():
    script_path = os.getcwd()
    print(script_path)
    print(os.path.dirname(__file__))
    with open(os.path.dirname(__file__) + '\\test_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test_001():
    with open(os.path.dirname(__file__) + '\\test_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test_002():
    csv_file =  open(os.path.dirname(__file__) + '\\test_data.csv', 'r')
    csv_sample = csv_file.read(1024)
    dialect = csv.Sniffer().sniff(csv_sample)
    #print(dialect)
    has_header = csv.Sniffer().has_header(csv_sample)
    print(has_header)                    
    csv_file.seek(0)
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    

def test_010():
    csv_adapter = CsvReadAdapter()
    csv_adapter.id = "CSV1"
    csv_adapter.all_at_once = True
    print(csv_adapter.config_options())
    

def test_020():
    
    buf1 = DictBuffer()
    buf1.id = "BSD_DATA"
    buf1.capacity = 500
    buf1.data_type = DataType.FLOAT.value
    buf1.description = "ball screw drive data"
    
    a1 = CsvReadAdapter()
    a1.id = "CSV1"
    a1.all_at_once = False
    a1.auto_detect = True
    a1.file_path = "tests\\data\\csv\\ballscrew_drive_data.csv"
    a1.force_numeric = True
    
    buffers : dict[str, Buffer] = BufferUtils.to_dict(buf1)
    
    addresses = None
    
    n = 1
    
    i = 0
    i_max = 100
    
    a1.install()
    if a1.connect():    
        while i < i_max:    
            a1.read_from_source(buffers, addresses, n)
            print(buffers["BSD_DATA"].data())
            time.sleep(0.05)
            i = i + 1
    else:
        assert False, "adapter did not connect"