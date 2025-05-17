import csv
import os


def test000():
    csv_file = open(os.path.dirname(__file__) + '\\test_data2.csv', 'w')
    csv_writer = csv.writer(csv_file, delimiter=";", lineterminator="\n")
    d = ("A", "B", "C")
    csv_writer.writerow(d)
    d = (1, 2, 3)
    csv_writer.writerow(d)
    d = ((4,5,6), (7,8,9))
    csv_writer.writerows(d)
    csv_file.close()