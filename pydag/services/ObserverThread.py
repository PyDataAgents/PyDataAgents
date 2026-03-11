from datetime import datetime
import threading
import time
from typing import Union
from zoneinfo import ZoneInfo
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from pydag.utils.TimeUtils import TimeUtils

from ..agents.AgentStates import AgentElementState, ServiceState
from .ObserverException import ObserverException
from .Observer import Observer
from .ThreadType import ThreadType
from .Service import Service


SAFETY_DIFF_TIME_UNITS : float = 1.0
SLEEP_WITH_HOLD_FACTOR : float = 0.9
    
class ObserverThread():
     
    def __init__(self, service : Service, observing_time : Union[int|str] = 0, thread_type : str = ThreadType.INSTANT.value, week_days : str = None):
        self._service : Service = service
        self._thread : threading.Thread = None
        self._lock : threading.RLock = threading.RLock()
        self._observers : list[Observer] = list()
        self._is_running : bool = False
        self._observing_time : Union[int|str] = observing_time
        self._thread_type : str = thread_type
        self._last_time : float = 0.0
        self._next_time : float = 0.0
        self._counts : int = 0
        self._week_days : str = week_days
        
        self._scheduler : Union[BlockingScheduler|BackgroundScheduler] = None        
               
        name = "Thread " + self._service.id
        match self._thread_type:
            case ThreadType.MILLI_SECOND.value:                    
                self._thread = threading.Thread(target = self._run_millisecond_thread, name=name)
            
            case ThreadType.MICRO_SECOND.value:
                self._thread = threading.Thread(target = self._run_microsecond_thread, name=name)
                
            case ThreadType.ONLY_ONCE.value:
                self._thread = threading.Thread(target = self._run_only_once_thread, name=name)
            
            case ThreadType.NANO_SECOND.value:
                self._thread = threading.Thread(target = self._run_nanosecond_thread, name=name)
                
            case ThreadType.SECOND.value:
                self._thread = threading.Thread(target = self._run_second_thread, name=name)
                                    
            case ThreadType.INSTANT.value:
                self._thread = threading.Thread(target = self._run_instant_thread, name=name)
                                
            case ThreadType.TRIGGERED.value:
                self._thread = threading.Thread(target = self._run_triggered_thread, name=name)
            
            case ThreadType.DATETIME.value:
                self._create_datetime_schedule()
                
            case ThreadType.DAYTIME.value:
                self._create_daytime_schedule()
                
            case ThreadType.EXPONENTIAL_SECOND.value:
                self._thread = threading.Thread(target = self._run_exponential_thread, name=name)
                    
            case _:
                self._thread = threading.Thread(target = self._run_millisecond_thread, name=name)
    
    def add_observer(self, observer : Observer):
        """ adds a new `Observer` to `ObserverThread`        

        Args:
            observer (Observer): `Observer` object
        """
        self._observers.append(observer)
        
    def run(self):
        """ run the `ObserverThread` logic in a separate thread        
        """        
        if len(self._observers) > 0:
            if not self._is_running:
                # exclude TRIGGERED threads from being started
                if self._thread_type != ThreadType.TRIGGERED.value:
                    with self._lock:
                        # important set running to True , so that the timed thread loops start running         
                        self._is_running = True                
                    if self._scheduler is not None:
                        self._scheduler.start()
                    elif self._thread is not None:
                        self._thread.start()
                    else:
                        raise ObserverException(f"could not start {self.__class__.__name__} for {self._service.__class__.__name__}, because no thread or scheduler was defined for thread type {self._thread_type}")
            else:
                raise ObserverException(f"could not start {self.__class__.__name__}, because it is running already")
        else:
            raise ObserverException(f"no {Observer.__class__.__name__ }s were added to {self.__class__.__name__}")
    
    def terminate(self):
        """ terminate the `ObserverThread`
        """
        with self._lock:
            self._is_running = False
            if self._scheduler is not None:
                self._scheduler.shutdown()
        self.denotify_observers()
    
    def notify_observers(self):
        """
        Docstring for notify_observers
                
        Raises:
            ObserverException: if an error during observe occurs
        """        
        for observer in self._observers:
            observer.observe()
    
    def denotify_observers(self):
        """
        
        Raises:
            ObserverException: if an error during unobserve occurs
        """
        for observer in self._observers:
            observer.unobserve()
        
    def _run_millisecond_thread(self):
        """
        
        """
        self._last_time = 0
        current_time = 0
        diff = 0
        #last_time = round(time.time() * 1000) # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_time = round(time.time() * 1000)
            if current_time - self._last_time >= self._observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = round(time.time() * 1000)
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._set_service_state(AgentElementState.ERROR)
            else:
                # do nothing and sleep a little
                diff = self._observing_time - SAFETY_DIFF_TIME_UNITS - (current_time - self._last_time)
                time.sleep(diff / 1000.0 * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped")         
    
    def _run_microsecond_thread(self):
        self._last_time = 0
        current_timer = 0
        last_timer = -1e15
        diff = 0
        #self._last_time = round(time.time() * 1000000.0) # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_timer = time.perf_counter_ns() / 1000
            if current_timer - last_timer >= self._observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time_ns() / 1000                    
                    last_timer = current_timer 
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._set_service_state(AgentElementState.ERROR)                   
            else:
                # do nothing and sleep a little
                diff = self._observing_time - SAFETY_DIFF_TIME_UNITS - (current_timer - last_timer)
                time.sleep(diff / 1000000.0 * SLEEP_WITH_HOLD_FACTOR)       
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
    
    def _run_nanosecond_thread(self):
        self._last_time = 0
        diff = 0
        last_timer = -1e15
        c = 0
        while self._is_running:
            current_timer = time.perf_counter_ns()
            #print(c)
            #print(current_timer - last_timer)
            if current_timer - last_timer >= self._observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time_ns()
                    last_timer = current_timer
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._set_service_state(AgentElementState.ERROR)
            else:
                # do nothing and sleep a little
                diff = self._observing_time - SAFETY_DIFF_TIME_UNITS - (current_timer - last_timer)
                time.sleep(diff / 1000000000.0 * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
        
    def _run_second_thread(self):
        self._last_time = 0
        current_time = 0
        diff = 0
        #self._last_time = time.time() # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_time = time.time()
            if current_time - self._last_time >= self._observing_time - SAFETY_DIFF_TIME_UNITS / 10.0:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time()
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._set_service_state(AgentElementState.ERROR)
            else:
                # do nothing and sleep a little
                diff = self._observing_time - SAFETY_DIFF_TIME_UNITS / 10.0 - (current_time - self._last_time)
                time.sleep(diff * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
    
    def _run_instant_thread(self):
        self._last_time = time.time_ns()
        while self._is_running:
            try:
                self.notify_observers()
                self._counts += 1
                self._last_time = time.time_ns()   
            except ObserverException as e:
                logger.error(e)
                with self._lock:
                    self._is_running = False
                self._set_service_state(AgentElementState.ERROR)   
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
    
    def _run_only_once_thread(self):
        self.notify_observers()
        self._last_time = time.time()
        self._counts += 1
        with self._lock:
            self._is_running = False
        self._set_service_state(ServiceState.STOPPED)
        
    def _run_triggered_thread(self):
        """ a triggered does nothing and its connected observers must be notified from the outside of this class
        """
        return
    
    def _create_datetime_schedule(self):
        self._scheduler = BackgroundScheduler()
        dt : datetime = TimeUtils.str_to_datetime(self._observing_time, dformat="%Y-%m-%d %H:%M:%S")
        self._scheduler.add_job(self.notify_observers, trigger='date', run_date=dt, id = "Scheduled-Job " + self._service.id)               
    
    def _create_daytime_schedule(self):
        local_tz = datetime.now().astimezone().tzinfo
        self._scheduler = BackgroundScheduler(timezone=local_tz)
        if self._observing_time.count(":") == 1:
            dt : datetime = TimeUtils.str_to_datetime(self._observing_time, dformat="%H:%M")
            hour : int = dt.hour
            minute : int = dt.minute
            self._scheduler.add_job(self.notify_observers, trigger='cron', day_of_week=self._week_days, hour=hour, minute=minute, id = "Scheduled-Job " + self._service.id)                
        elif self._observing_time.count(":") == 2:
            dt : datetime = TimeUtils.str_to_datetime(self._observing_time, dformat="%H:%M:%S")
            hour : int = dt.hour
            minute : int = dt.minute
            second : int = dt.second
            self._scheduler.add_job(self.notify_observers, trigger='cron', day_of_week=self._week_days, hour=hour, minute=minute, second=second, id = "Scheduled-Job " + self._service.id)
        else:
            raise ObserverException("Wrong dateformat in observingtime " + self._observing_time)       
    
    def _run_exponential_thread(self):
        self._last_time = 0
        current_time = 0
        diff = 0
        #self._last_time = time.time() # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_time = time.time()
            if current_time - self._last_time >= self._observing_time - SAFETY_DIFF_TIME_UNITS / 10.0:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time()                    
                    self._observing_time = 2 * self._observing_time
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._set_service_state(AgentElementState.ERROR)
            else:
                # do nothing and sleep a little
                diff = self._observing_time - SAFETY_DIFF_TIME_UNITS / 10.0 - (current_time - self._last_time)
                time.sleep(diff * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped")
            
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running
    
    def get_last_update(self) -> float:
        return self._last_time

    def get_counts(self) -> int:
        return self._counts
    
    def _set_service_state(self, state : Union[AgentElementState, ServiceState]):
        self._service.set_state(state)
    