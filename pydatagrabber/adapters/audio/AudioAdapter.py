from dataclasses import dataclass, field
import time
import sounddevice as sd
import numpy as np
from PyDataGrabber.pydatagrabber.adapters.SubscribeAdapter import SubscribeAdapter
from PyDataGrabber.pydatagrabber.buffers.Buffer import Buffer

@dataclass
class AudioAdapter(SubscribeAdapter):

    sample_rate : int = field(default=44_100, metadata={"description": "sample rate of audio channel, usually 44100 Hz"})
    device : int = field(default=None, metadata={"description": "device number to use as input stream, if nothing is specified the default device is used"})

    def __init__(self):
        super().__init__()
        self.subscribing = False

    def connect(self) -> bool:
        d = sd.query_devices(None, 'input')
        self.LOGGER.debug(d)
        if len(d) > 0:
            return True
        else:
            return False

    def disconnect(self) -> bool:
        return True

    def subscribe(self, buffers : dict[str, Buffer], addresses : list[str] = None, sampling_period : int = 0, n : int = 1024):
        self.subscribing = True
        buf = buffers.values()[0]

        def audio_callback(indata : np.ndarray, frames, time, status):
            if status:
                self.LOGGER.error("Audio Stream status: ", status)
            buf.push(indata.tolist())

        with sd.InputStream(callback=audio_callback,
                            channels=1,
                            samplerate=self.sample_rate,
                            blocksize=n):
            while self.subscribing:
                time.sleep(1)
            self.LOGGER.debug(self.name() + " stopped subscribing to audio channel")

    def unsubscribe(self):
        self.subscribing = False
