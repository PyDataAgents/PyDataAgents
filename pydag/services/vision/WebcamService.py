import base64
from dataclasses import dataclass, field
import cv2


from ...buffers.Buffer import Buffer
from ..ServiceException import ServiceException
from ..ReadService import ReadService
from ...agents.Agent import Agent


@dataclass
class WebcamService(ReadService):
    """ An `MappingService` that captures webcam video feed into a `Buffer`
    """
    
    camera_index : int = field(default=0, metadata={"description": "indexof installed cameras"})
    resolution : list[int] = field(default_factory=list, metadata={"description": "resolution [width, height]"})
    fps : int = field(default=30, metadata={"description": "frames per second"})
    codec : str = field(default="MJPG", metadata={"description": "video codec to use, mp4v | MJPG | H264 | XVID"})
    encode_base64 : bool = field(default=False, metadata={"description": "if set to true, the image data is converted to base64 strings"})
    data_uri_prefix : str = field(default="data:image/jpeg;base64,", metadata = {"description": "data URI prefix for base64 images"})
    
    def __post_init__(self):
        super().__post_init__()
        self._vc = None
        self._codec = None
            
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._vc = cv2.VideoCapture(self.camera_index)
        if len(self.resolution) == 0:
            self._autodetect_resolution()
        self._vc.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self._vc.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self._vc.set(cv2.CAP_PROP_FPS, self.fps)
        self._codec = cv2.VideoWriter.fourcc(*self.codec)
        if not self._vc.isOpened():
            raise ServiceException("Video Capture is not open")
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall()
        self._vc.release()
        self._vc = None
        self._codec = None
            
    def _read_from_source(self):
        if len(self.get_buffers()) > 1:
            raise ServiceException(f"only 1 {Buffer.cname()} can be used for data storage")
        else:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            ret, frame = self._vc.read()
            #print(type(frame))
            if self.encode_base64:
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                success, img_buf = cv2.imencode(".jpg", frame, encode_params)
                if success:
                    s : str = None
                    if self.data_uri_prefix is not None:
                        s = self.data_uri_prefix + base64.b64encode(img_buf).decode("utf-8")
                    else:
                        s = base64.b64encode(img_buf).decode("utf-8")
                    buffer.push(s)
                else:
                    raise ServiceException(f"could not encode image as base64 string in {WebcamService.cname()}")
            else:
                # here because of image data a numpy array is pushed to buffer as list element            
                buffer.push(frame)
       
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
            raise ServiceException("Could not autodetect frame resolution")        
    