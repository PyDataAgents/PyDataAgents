from dataclasses import dataclass, field
import os

from pydag.services.datamodel.DataModel import DataModel

@dataclass
class AudioDataModel(DataModel):
    """ Test Audio DataModel """
    
    aud : str = field(default=os.path.dirname(__file__) + os.sep + "audio_example.mp3", metadata={"description": "an example audio player", "ui_type": "audio", "ui_options": {"controls": True, "autoplay": True, "loop": True}})