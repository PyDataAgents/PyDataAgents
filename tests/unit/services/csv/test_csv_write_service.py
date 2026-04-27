import csv
import os

from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.csv.CsvWriteService import CsvWriteService


def test_000():
    csv_file = open(os.path.dirname(__file__) + '\\test_data2.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(csv_file, delimiter=";", lineterminator="\n")
    d = ("A", "B", "C")
    csv_writer.writerow(d)
    d = (1, 2, 3)
    csv_writer.writerow(d)
    d = ((4,5,6), (7,8,9))
    csv_writer.writerows(d)
    csv_file.close()
    
def test_010():
    buf = DictBuffer(id="B1")
    buf.install()
    buf.push({"A": 1, "B": 2, "C": 3})
    buf.push({"A": 4, "B": 5, "C": 6})
    buf.push({"A": 7, "B": 8, "C": 9})
    
    folder = os.path.dirname(__file__)
    
    csv = CsvWriteService(folder=folder,
                          file_post_fix="test",
                          file_extension="csv",
                          delimiter=";",
                          thread_type=ThreadType.MILLI_SECOND.value,
                          n=1)
    
    csv.add_buffer(buf)
    csv.install()
    
    for _ in range(1, 4):
        csv._write_to_sink()
        
    csv.uninstall()