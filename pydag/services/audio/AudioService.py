from dataclasses import dataclass, field
import sounddevice as sd
import numpy as np
from loguru import logger


from ..SubscribeService import SubscribeService
from ...agents.Agent import Agent
from ..ServiceException import ServiceException


@dataclass
class AudioService(SubscribeService):
    """`SubscribeService` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.
    """

    sample_rate : int = field(default=44100, metadata={"description": "sample rate of audio channel, usually 44100 Hz"})
    device : int = field(default=None, metadata={"description": "device number to use as input stream, if nothing is specified the default device is used"})

    def __post_init__(self):
        super().__post_init__()
        self._stream : sd.InputStream = None

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        d = sd.query_devices(None, 'input')
        logger.debug(d)
        if len(d) == 0:
            raise ServiceException("No audio input devices found")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self._stream is not None:
            self._stream.close()

    def _subscribe(self):
        buf = next(iter(self._buffers.values()))

        def audio_callback(indata : np.ndarray, frames, time, status):
            if status:
                logger.error("Audio Stream status: ", status)
            buf.push(indata.ravel().tolist())

        self._stream = sd.InputStream(callback=audio_callback,
                            channels=1,
                            samplerate=self.sample_rate,
                            blocksize=self.n)
        self._stream.start()

    def _unsubscribe(self):
        if self._stream is not None:
            self._stream.stop()
