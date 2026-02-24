from dataclasses import dataclass, field
import time
import sounddevice as sd
import numpy as np
from loguru import logger


from ...agents.Agent import Agent
from ...adapters.SubscribeAdapter import SubscribeAdapter
from ...buffers.Buffer import Buffer


@dataclass
class AudioAdapter(SubscribeAdapter):
    """`Adapter` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.
    """

    sample_rate : int = field(default=44_100, metadata={"description": "sample rate of audio channel, usually 44100 Hz"})
    device : int = field(default=None, metadata={"description": "device number to use as input stream, if nothing is specified the default device is used"})

    def __post_init__(self):
        super().__post_init__()
        self._stream : sd.InputStream = None

    def _on_install(self, agent : Agent = None):
        return
        
    def _on_uninstall(self, agent : Agent = None):
        return

    def _on_connect(self) -> bool:
        d = sd.query_devices(None, 'input')
        logger.debug(d)
        if len(d) > 0:
            return True
        else:
            return False

    def _on_disconnect(self) -> bool:
        if self._stream is not None:
            self._stream.close()
        return True

    def _on_subscribe(self, buffers : dict[str, Buffer], addresses : list[str] = None, sampling_period : int = 0, n : int = 1024):
        buf = next(iter(buffers.values()))

        def audio_callback(indata : np.ndarray, frames, time, status):
            if status:
                logger.error("Audio Stream status: ", status)
            buf.push(indata.ravel().tolist())

        self._stream = sd.InputStream(callback=audio_callback,
                            channels=1,
                            samplerate=self.sample_rate,
                            blocksize=n)
        self._stream.start()

    def _on_unsubscribe(self):
        self._stream.stop()
