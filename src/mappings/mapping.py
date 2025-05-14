import threading
import time
import enum
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

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
    SUB = "SUB"
    PUB = "PUB"

class Mapping(GrabberElement):

    SAFETY_DIFF_TIME_UNITS = 1
    SLEEP_WITH_HOLD_FACTOR = 0.9

    def __init__(self, id):
        super().__init__(id)
        self.buffers = {}
        self.adapter = None
        self.addresses = list()
        self.thread_type = ThreadType.MILLI_SECOND
        self.sampling_period = 0
        self.mapping_type = None
        self.persistent = True
        self.isRunning = False
        self.hasError = False
        self.lastActiveTime = 0
        self.thread = None
        self.lock = threading.RLock()

    def thread_type(self, thread_type = ThreadType.MILLI_SECOND):
        self.thread_type = thread_type
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

    def sampling_period(self, sampling_period : int):
        self.sampling_period = sampling_period
        return self 
    
    def persistent(self, persistent : bool = True):
        self.persistent = persistent
        return self
    
    def mapping_type(self, mapping_type : MappingType):
        self.mapping_type = mapping_type
        return self
    
    def start(self):
        if not self.isRunning:
            match self.thread_type:
                case ThreadType.MILLI_SECOND:                    
                    self.thread = threading.Thread(target = self.runMillisecondThread)
                
                case ThreadType.MICRO_SECOND:
                    self.thread = threading.Thread(target = self.runMicrosecondThread)
                    
                case ThreadType.ONLY_ONCE:
                    self.thread = threading.Thread(target = self.runOnlyOnceThread)
                    
                case _:
                    self.thread = threading.Thread(target = self.runMillisecondThread)
                        
            self.isRunning = True            
            self.thread.start()
        else:
            Mapping.LOGGER.error("could not start mapping, because it is running already")
        
    def stop(self):
        self.LOGGER.info("Stopping Mapping " + self.id)
        self.isRunning = False
        match self.mapping_type:
            case MappingType.SUB:
                self.adapter.unsubscribe()
                
            case MappingType.PUB:
                self.adapter.unpublish()                
        
        
    def runMillisecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = round(time.time() * 1000)
        while self.isRunning:
            current_time = round(time.time() * 1000)
            if current_time - last_time > self.sampling_period - self.SAFETY_DIFF_TIME_UNITS:
                match self.mapping_type:
                    case MappingType.READ:
                        self.adapter.readFromSource(self.buffers, self.addresses, self.sampling_period)
                            
                    case MappingType.WRITE:
                        self.adapter.writeToSink(self.buffers, self.addresses, self.sampling_period, self.persistent)
                last_time = round(time.time() * 1000)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - self.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000.0 * self.SLEEP_WITH_HOLD_FACTOR)
        
        self.LOGGER.info("Mapping " + self.id + " has stopped")   
        
    
    def runMicrosecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = round(time.time() * 1000000.0)
        while self.isRunning:
            current_time = round(time.time() * 1000000.0)
            if current_time - last_time > self.sampling_period - self.SAFETY_DIFF_TIME_UNITS:
                match self.mapping_type:
                    case MappingType.READ:
                        self.adapter.readFromSource(self.buffers, self.addresses, self.sampling_period)
                            
                    case MappingType.WRITE:
                        self.adapter.writeToSink(self.buffers, self.addresses, self.sampling_period, self.persistent)
                last_time = round(time.time() * 1000000.0)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - self.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000000.0 * self.SLEEP_WITH_HOLD_FACTOR)
        
        self.LOGGER.info("Mapping " + self.id + " has stopped")
        pass
    
    def runOnlyOnceThread(self):
        self.isRunning = True
        match self.mapping_type:
            case MappingType.SUB:
                self.adapter.subscribe(self.buffers, self.addresses, self.sampling_period)
                
            case MappingType.PUB:
                self.adapter.publish(self.buffers, self.addresses, self.sampling_period, self.persistent)
    