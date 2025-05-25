import csv
import os
from PyDataGrabber.adapters.csv.CsvReadAdapter import CsvReadAdapter

def test000():
    script_path = os.getcwd()
    print(script_path)
    print(os.path.dirname(__file__))
    with open(os.path.dirname(__file__) + '\\test_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test001():
    with open(os.path.dirname(__file__) + '\\test_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            print(row)
            
def test002():
    csv_file =  open(os.path.dirname(__file__) + '\\test_data.csv', 'r')
    csv_sample = csv_file.read(1024)
    dialect = csv.Sniffer().sniff(csv_sample)
    #print(dialect)
    has_header = csv.Sniffer().has_header(csv_sample)
    print(has_header)                    
    csv_file.seek(0)
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    

def test010():
    csv_adapter = CsvReadAdapter()
    csv_adapter.id = "CSV1"
    csv_adapter.all_at_once = True
    print(csv_adapter.config_options())
    
    