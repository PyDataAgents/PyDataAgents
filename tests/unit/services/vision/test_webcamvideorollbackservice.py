import os
import time
import cv2

from pydag.services.vision.WebcamVideoRollbackService import WebcamVideoRollbackService
from pydag.utils.FileUtils import FileUtils

def test_000(): 
    print(cv2.__file__)
    print(cv2.VideoWriter)
    print(cv2.VideoCapture)
    
def test_webcam_rollback_service():
    folder = os.path.dirname(__file__) + os.sep + "video"
    vlen = 1 * 60
    rb = 5
    
    wvrs = WebcamVideoRollbackService(
        output_folder=folder,
        rollback_files=rb,
        video_length=vlen,
        codec="mp4v",
        extension="mp4"
    )
    
    wvrs.install()
    
    wvrs.start()
    
    time.sleep(rb * vlen * 2)
    
    wvrs.stop()
    
    f = len(FileUtils.list_files(folder))
    assert f == rb + 1, "Number of rollback files is not present"
    
    