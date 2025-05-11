from abc import abstractmethod
import threading
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
import enum

class ThreadType(enum.Enum):
    MILLI_SECOND = "MILLI_SECOND"
    MICRO_SECOND = "MICRO_SECOND"
    NANO_SECOND = "NANO_SECOND"
    SECOND = "SECOND"
    ONLY_ONCE = "ONLY_ONCE"
    TRIGGERED = "TRIGGERED"

class MappingType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    SUBSCRIPTION = "SUB"
    PUB = "PUB"

class Mapping(GrabberElement, threading.thread):

    def __init__(self):
        super().__init__(Mapping.unique_id())
        self.buffers = {}
        self.adapter = None
        self.addresses = list()
        self.threadType = ThreadType.MILLI_SECOND
        self.sampling_period = 0

    def threadType(self, type = ThreadType.MILLI_SECOND):
        self.threadType = type
        return self

    def buffer(self, buffer: Buffer):
        self.buffers.update(buffer.id, buffer)
        return self

    def buffers(self, buffers: dict):
        self.buffers = buffers
        return self

    def address(self, address: str):
        self.addresses.append(address)
        return self

    def addresses(self, addresses: list):
        self.addresses = addresses
        return self 

    def adapter(self, adapter: Adapter):
        self.adapter = adapter
        return self

    def sampling_period(self, sampling_period : int = 0):
        self.sampling_period = sampling_period
        return self   

    @abstractmethod
    def run(self):
        pass
