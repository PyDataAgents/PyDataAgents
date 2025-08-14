from dataclasses import dataclass, field
import threading
import time
from ..agents.AgentElement import AgentElement
from .Observer import Observer
from .ThreadType import ThreadType


@dataclass
class ObserverThread(AgentElement):
        
    sampling_period : int = field(default=0, metadata={"description": "sampling period between observer notifies"})
    thread_type : str = field(default=ThreadType.MILLI_SECOND.value, metadata={"description": "type of thread -> MILLI_SECOND | MICRO_SECOND | NANO_SECOND | SECOND | ONLY_ONCE | INSTANT | TRIGGERED"})
    
    SAFETY_DIFF_TIME_UNITS : int = 1
    SLEEP_WITH_HOLD_FACTOR : float = 0.9
     
    def __post_init__(self):
        super().__post_init__()
        self.thread : threading.Thread = None
        self.observers : list[Observer] = list()
        self.is_running = False
        
    def add_observer(self, observer : Observer):
        self.observers.append(observer)
        
    def start(self):        
        if len(self.observers) > 0:
            if not self.is_running:
                name = "Thread " + self.id
                match self.thread_type:
                    case ThreadType.MILLI_SECOND.value:                    
                        self.thread = threading.Thread(target = self.runMillisecondThread, name=name)
                    
                    case ThreadType.MICRO_SECOND.value:
                        self.thread = threading.Thread(target = self.runMicrosecondThread, name=name)
                        
                    case ThreadType.ONLY_ONCE.value:
                        self.thread = threading.Thread(target = self.runOnlyOnceThread, name=name)
                    
                    case ThreadType.NANO_SECOND.value:
                        self.thread = threading.Thread(target = self.runNanosecondThread, name=name)
                        
                    case ThreadType.SECOND.value:
                        self.thread = threading.Thread(target = self.runSecondThread, name=name)
                                            
                    case ThreadType.INSTANT.value:
                        self.thread = threading.Thread(target = self.runInstantThread, name=name)
                                        
                    case ThreadType.TRIGGERED:
                        self.thread = threading.Thread(target = self.runTriggeredThread, name=name)
                        
                    case _:
                        self.thread = threading.Thread(target = self.runMillisecondThread, name=name)
                
                # important set running to True , so that the timed thread loops start running         
                self.is_running = True
                # exclude TRIGGERED threads from being started
                if self.thread_type is not ThreadType.TRIGGERED.value:
                    self.thread.start()
            else:
                ObserverThread.LOGGER.error("could not start " +  self.__class__.__name__ + ", because it is running already")
        else:
            ObserverThread.LOGGER.error("no " + Observer.__class__.__name__ + " s were added to this " + self.__class__.__name__)
    
    def stop(self):
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] is being stopped")
        self.is_running = False
        self.denotify_observers()
    
    def notify_observers(self):
        for observer in self.observers:
            observer.observe()
    
    def denotify_observers(self):
        for observer in self.observers:
            observer.unobserve()
        
    def runMillisecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = round(time.time() * 1000)
        while self.is_running:
            current_time = round(time.time() * 1000)
            if current_time - last_time > self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS:
                self.notify_observers()
                last_time = round(time.time() * 1000)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000.0 * ObserverThread.SLEEP_WITH_HOLD_FACTOR)        
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")         
    
    def runMicrosecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = round(time.time() * 1000000.0)
        while self.is_running:
            current_time = round(time.time() * 1000000.0)
            if current_time - last_time > self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS:
                self.notify_observers()
                last_time = round(time.time() * 1000000.0)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000000.0 * ObserverThread.SLEEP_WITH_HOLD_FACTOR)        
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")
    
    def runNanosecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = round(time.time() * 1000000000.0)
        while self.is_running:
            current_time = round(time.time() * 1000000000.0)
            if current_time - last_time > self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS:
                self.notify_observers()
                last_time = round(time.time() * 1000000000.0)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000000000.0 * ObserverThread.SLEEP_WITH_HOLD_FACTOR)        
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")
        
    def runSecondThread(self):
        last_time = 0
        current_time = 0
        diff = 0
        last_time = time.time()
        while self.is_running:
            current_time = time.time()
            if current_time - last_time > self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS:
                self.notify_observers()
                last_time = time.time()
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff * ObserverThread.SLEEP_WITH_HOLD_FACTOR)        
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")
    
    def runInstantThread(self):
        last_time = round(time.time() * 1000000.0)
        while self.is_running:
            self.notify_observers()
            last_time = round(time.time() * 1000000.0)       
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")
    
    def runOnlyOnceThread(self):
        self.notify_observers()
        
    def runTriggeredThread(self):
        # do thing
        self.is_running = False
    