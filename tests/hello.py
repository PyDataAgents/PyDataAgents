import os
import sys

from pathlib import Path

current_dir = Path(__file__)
print(current_dir)

print(sys.path[1])
#from PyDataGrabber.src.buffers.ListBuffer import ListBuffer

msg = "Roll a dice!"
print(msg)

#buf = ListBuffer("B1", 100)
#print(buf)

print(os.getcwd())