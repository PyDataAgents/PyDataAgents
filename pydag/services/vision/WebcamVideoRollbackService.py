from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import os
from pathlib import Path
import threading
import time
import cv2
from loguru import logger

from ...agents.Agent import Agent
from ...utils.FileUtils import FileUtils
from ...services.ServiceException import ServiceException
from ...services.Service import Service
from ...agents.AgentStates import ServiceState


@dataclass
class WebcamVideoRollbackService(Service):
    """ A `Service` that captures webcam video feed into video files on filesystem for x seconds
    and continuously creates new files,
    additionally only the y last files are being kept before being deleted
    """
    
    output_folder : str = field(default=None, metadata={"description": "folder path to the video output folder"})
    post_fix : str = field(default="video", metadata={"description": "postfix to append to each file, all the files start with timestamp"})
    extension : str = field(default="avi", metadata={"description": "specifies the extension of the video file, this should match with the selected codec. mp4 -> mp4v, avi -> MJPG, ..."})
    video_length : float = field(default=60, metadata={"description": "video length in seconds"})
    rollback_files : int  = field(default=10, metadata={"description": "number of rollback files to keep"})
    camera_index : int = field(default=0, metadata={"description": "index of installed cameras"})
    resolution : list[int] = field(default_factory=list, metadata={"description": "resolution [width, height]"})
    fps : int = field(default=30, metadata={"description": "frames per second"})
    codec : str = field(default="MJPG", metadata={"description": "video codec to use, mp4v | MJPG | H264 | XVID"})
    
    def __post_init__(self):
        super().__post_init__()
        self._vc = None
        self._files : deque = None
        self._codec = None
        self._service_thread : threading.Thread = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._vc = cv2.VideoCapture(self.camera_index)
        if len(self.resolution) == 0:
            self._autodetect_resolution()
        self._vc.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self._vc.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self._vc.set(cv2.CAP_PROP_FPS, self.fps)
        self._files = deque()
        self._codec = cv2.VideoWriter.fourcc(*self.codec)
        if not self._vc.isOpened():
            raise ServiceException("No Video Capture could be opened with index " + str(self.camera_index))
        if not FileUtils.exists_folder(self.output_folder):
            logger.debug("Output folder " + self.output_folder + " does not exist, creating it.")
            FileUtils.create_dir(self.output_folder)
       
    def _autodetect_resolution(self):
        # Try real frame first
        ret, frame = self._vc.read()
        if ret:
            h, w = frame.shape[:2]
            self.resolution =[w, h]
            return

        # Fallback to CAP_PROP
        w = int(self._vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if w > 0 and h > 0:
            self.resolution =[w, h]
        else:
            raise ServiceException("")
    
    def _new_filename(self) -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{self.output_folder}{os.sep}{ts}_{self.post_fix}.{self.extension}"
    
    def _cleanup_old_files(self):
        while len(self._files) > self.rollback_files:
            old : str = self._files.popleft()
            if FileUtils.exists_file(old):
                FileUtils.delete_file(old)
    
    def _on_start(self):
        # collect all files, that are already in folder on startup
        self._files = deque(FileUtils.list_files(self.output_folder))
        
        # start thread in background
        self._service_thread = threading.Thread(target=self._run, name=f"Thread-{self.id}")
        self._service_thread.start()
    
    def _on_stop(self):
        return
        
    def _run(self):
        while self._state == ServiceState.RUNNING:
            filename = self._new_filename()
            writer = cv2.VideoWriter(
                    filename,
                    self._codec,
                    self.fps,
                    self.resolution,
                )

            start_time = time.time()
            while time.time() - start_time < self.video_length:
                ret, frame = self._vc.read()
                if not ret:
                    break
                writer.write(frame)

            writer.release()
            self._files.append(filename)
            self._cleanup_old_files()
        
        self._vc.release()
        cv2.destroyAllWindows()
            