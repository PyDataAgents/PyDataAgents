import threading
import time
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.mappings.Mapping import Mapping, ThreadType
from PyDataGrabber.src.mappings.Observer import Observer


class ObserverThread(GrabberElement):
    
    SAFETY_DIFF_TIME_UNITS : int = 1
    SLEEP_WITH_HOLD_FACTOR : float = 0.9
     
    def __init__(self, thread_type = Mapping.ThreadType.MILLI_SECOND, id : str = None):
        super().__init__(id)
        self.thread_type : Mapping.ThreadType = thread_type
        self.thread : threading.thread = None
        self.observers : list[Observer] = list()
        
    def add_observer(self, observer : Observer):
        self.observers.append(observer)
        
    def start(self):
        if len(self.observers) > 0:
            if not self.isRunning:
                match self.thread_type:
                    case Mapping.ThreadType.MILLI_SECOND:                    
                        self.thread = threading.Thread(target = self.runMillisecondThread, name="Thread " + id)
                    
                    case Mapping.ThreadType.MICRO_SECOND:
                        self.thread = threading.Thread(target = self.runMicrosecondThread, name="Thread " + id)
                        
                    case Mapping.ThreadType.ONLY_ONCE:
                        self.thread = threading.Thread(target = self.runOnlyOnceThread, name="Thread " + id)
                        
                    case _:
                        self.thread = threading.Thread(target = self.runMillisecondThread, name="Thread " + id)
                            
                self.isRunning = True            
                self.thread.start()
            else:
                ObserverThread.LOGGER.error("could not start " +  self.__class__.__name__ + ", because it is running already")
        else:
            ObserverThread.LOGGER.error("no " + Observer.__class__.__name__ + " s were added to this " + self.__class__.__name__)
    
    def stop(self):
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] is being stopped")
        self.isRunning = False
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
        while self.isRunning:
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
        while self.isRunning:
            current_time = round(time.time() * 1000000.0)
            if current_time - last_time > self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS:
                self.notify_observers()
                last_time = round(time.time() * 1000000.0)
            else:
                # do nothing and sleep a little
                diff = self.sampling_period - ObserverThread.SAFETY_DIFF_TIME_UNITS - (current_time - last_time)
                time.sleep(diff / 1000000.0 * ObserverThread.SLEEP_WITH_HOLD_FACTOR)
        
        ObserverThread.LOGGER.info(self.__class__.__name__ + "[" + self.id + "] has stopped")
    
    def runOnlyOnceThread(self):
        self.notify_observers()
    