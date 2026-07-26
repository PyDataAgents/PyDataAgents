from dataclasses import dataclass, field
import os

from pydag.services.datamodel.DataModel import DataModel

@dataclass
class VideoDataModel(DataModel):
    """ Test Video DataModel """
    
    vid : str = field(default=os.path.dirname(__file__) + os.sep + "video_example.mp4", metadata={"ui_type": "video", "ui_options": {"controls": True, "autoplay": True, "loop": True}})