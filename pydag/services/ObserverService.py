from __future__ import annotations
from dataclasses import dataclass, field
import threading
from datetime import datetime
import time
from typing import TYPE_CHECKING, Optional, Union
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.job import Job
from loguru import logger


from ..agents.AgentConfig import AgentConfig
from ..agents.AgentStates import AgentElementState, ServiceState
from ..services.ServiceException import ServiceException
from ..utils.TimeUtils import TimeUtils
from .ThreadType import ThreadType
from .ObserverException import ObserverException
from .Service import Service
from .Observer import Observer


if TYPE_CHECKING:
    from ..agents.Agent import Agent


SAFETY_DIFF_TIME_UNITS : float = 1.0
SLEEP_WITH_HOLD_FACTOR : float = 0.9


@dataclass
class ObserverService(Service):
    """abstract base class for Services with ObserverThreads
    """
    
    thread_type : str = field(default=None, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ..."})    
    observing_time : Union[int|str] = field(default=None, metadata={"description": "observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ..."})    
    week_days : Optional[str] = field(default=None, metadata={"description": "specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6"})
       
    def __post_init__(self):
        super().__post_init__()
        self._thread : threading.Thread = None
        self._lock : threading.RLock = threading.RLock()
        self._observers : list[Observer] = list()
        self._is_running : bool = False
        self._last_time : float = 0.0
        self._next_time : float = 0.0
        self._counts : int = 0        
        self._scheduler : Union[BlockingScheduler|BackgroundScheduler] = None
        self._scheduled_job : Job = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        name = f"Thread-{self.__class__.__name__} {self.id}"
        match self.thread_type:
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
                self._thread = None
    
    def _on_uninstall(self, agent = None):
        super()._on_uninstall(agent)
        
    def add_observer(self, observer : Observer):
        """ adds a new `Observer` to `ObserverThread`        

        Args:
            observer (Observer): `Observer` object
        """
        self._observers.append(observer)
        
    def _on_start(self):
        """ run the logic in a separate thread        
        """
        if len(self._observers) > 0:
            if not self._is_running:
                # exclude TRIGGERED threads from being started
                if self.thread_type != ThreadType.TRIGGERED.value:
                    with self._lock:
                        # important set running to True , so that the timed thread loops start running         
                        self._is_running = True                
                    if self._scheduler is not None:
                        self._scheduler.start()
                        dt : datetime = self._scheduled_job.next_run_time
                        self._next_time = TimeUtils.datetime_to_utc(dt)
                    elif self._thread is not None:
                        self._thread.start()
                    elif self.thread_type == ThreadType.DAEMON.value:
                        self._run_daemon_observers()
                    else:
                        raise ServiceException(f"could not start {self.__class__.__name__}, because no thread or scheduler was defined for thread type {self.thread_type}")
            else:
                raise ServiceException(f"could not start {self.__class__.__name__}, because it is running already")
        else:
            raise ServiceException(f"no {Observer.__class__.__name__ }s were added to {self.__class__.__name__}")
    
    def _on_stop(self):
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
            if current_time - self._last_time >= self.observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = round(time.time() * 1000)
                    self._next_time = self._last_time + self.observing_time
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._state = AgentElementState.ERROR
            else:
                # do nothing and sleep a little
                diff = self.observing_time - SAFETY_DIFF_TIME_UNITS - (current_time - self._last_time)
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
            if current_timer - last_timer >= self.observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1                   
                    last_timer = current_timer
                    self._last_time = time.time_ns() / 1000 
                    self._next_time = self._last_time + self.observing_time 
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._state = AgentElementState.ERROR                   
            else:
                # do nothing and sleep a little
                diff = self.observing_time - SAFETY_DIFF_TIME_UNITS - (current_timer - last_timer)
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
            if current_timer - last_timer >= self.observing_time - SAFETY_DIFF_TIME_UNITS:
                try:
                    self.notify_observers()
                    self._counts += 1
                    last_timer = current_timer
                    self._last_time = time.time_ns()
                    self._next_time = self._last_time + self.observing_time
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._state = AgentElementState.ERROR
            else:
                # do nothing and sleep a little
                diff = self.observing_time - SAFETY_DIFF_TIME_UNITS - (current_timer - last_timer)
                time.sleep(diff / 1000000000.0 * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
        
    def _run_second_thread(self):
        self._last_time = 0
        current_time = 0
        diff = 0
        #self._last_time = time.time() # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_time = time.time()
            if current_time - self._last_time >= self.observing_time - SAFETY_DIFF_TIME_UNITS / 10.0:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time()
                    self._next_time = self._last_time + self.observing_time
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._state = AgentElementState.ERROR
            else:
                # do nothing and sleep a little
                diff = self.observing_time - SAFETY_DIFF_TIME_UNITS / 10.0 - (current_time - self._last_time)
                time.sleep(diff * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
    
    def _run_instant_thread(self):
        self._last_time = time.time_ns()
        while self._is_running:
            try:
                self.notify_observers()
                self._counts += 1
                self._last_time = time.time_ns()
                self._next_time = self._last_time
            except ObserverException as e:
                logger.error(e)
                with self._lock:
                    self._is_running = False
                self._state = AgentElementState.ERROR   
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped") 
    
    def _run_only_once_thread(self):
        try:
            self.notify_observers()
        except ObserverException as e:
            self._state = AgentElementState.ERROR
            logger.error(e)
        self._last_time = time.time()
        self._counts += 1
        with self._lock:
            self._is_running = False
        self._state = ServiceState.INSTALLED
        
    def _run_daemon_observers(self):
        try:
            self.notify_observers()
        except ObserverException as e:
            self._state = AgentElementState.ERROR
            logger.error(e)

    def _run_triggered_thread(self):
        """ a triggered does nothing and its connected observers must be notified from the outside of this class
        """
        return
    
    def _create_datetime_schedule(self):
        self._scheduler = BackgroundScheduler()
        dt : datetime = TimeUtils.str_to_datetime(self.observing_time, dformat="%Y-%m-%d %H:%M:%S")
        self._scheduled_job = self._scheduler.add_job(self.notify_observers, trigger='date', run_date=dt, id = "Scheduled-Job " + self.id)               
    
    def _create_daytime_schedule(self):
        local_tz = datetime.now().astimezone().tzinfo
        self._scheduler = BackgroundScheduler(timezone=local_tz)
        if self.observing_time.count(":") == 1:
            dt : datetime = TimeUtils.str_to_datetime(self.observing_time, dformat="%H:%M")
            hour : int = dt.hour
            minute : int = dt.minute
            self._scheduled_job = self._scheduler.add_job(self._daytime_task, trigger='cron', day_of_week=self.week_days, hour=hour, minute=minute, id = "Scheduled-Job " + self.id)         
        elif self.observing_time.count(":") == 2:
            dt : datetime = TimeUtils.str_to_datetime(self.observing_time, dformat="%H:%M:%S")
            hour : int = dt.hour
            minute : int = dt.minute
            second : int = dt.second
            self._scheduled_job = self._scheduler.add_job(self._daytime_task, trigger='cron', day_of_week=self.week_days, hour=hour, minute=minute, second=second, id = "Scheduled-Job " + self.id)
        else:
            raise ObserverException("Wrong dateformat in observingtime " + self.observing_time)       
    
    def _daytime_task(self):
        """ helper task for daytime schedule to set next_time and execute observers
        """
        self.notify_observers()
        dt : datetime = self._scheduled_job.next_run_time
        self._next_time = TimeUtils.datetime_to_utc(dt)
    
    def _run_exponential_thread(self):
        self._last_time = 0
        current_time = 0
        diff = 0
        #self._last_time = time.time() # if this line is uncommented, the first observer notify happens after 1 observing_time, otherwise immediately
        while self._is_running:
            current_time = time.time()
            if current_time - self._last_time >= self.observing_time - SAFETY_DIFF_TIME_UNITS / 10.0:
                try:
                    self.notify_observers()
                    self._counts += 1
                    self._last_time = time.time()                    
                    self.observing_time = 2 * self.observing_time
                    if self.observing_time > AgentConfig.MAX_EXPONENTIAL_SECONDS:
                        self.observing_time = AgentConfig.MAX_EXPONENTIAL_SECONDS
                    self._next_time = self._last_time + self.observing_time
                except ObserverException as e:
                    logger.error(e)
                    with self._lock:
                        self._is_running = False
                    self._state = AgentElementState.ERROR
            else:
                # do nothing and sleep a little
                diff = self.observing_time - SAFETY_DIFF_TIME_UNITS / 10.0 - (current_time - self._last_time)
                time.sleep(diff * SLEEP_WITH_HOLD_FACTOR)        
        logger.info(f"{self.__class__.__name__} [{self._thread.name}] has stopped")
            
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running
    
    def get_last_update(self) -> float:
        """ returns the timestamp of the last `ObserverThread` iteration in ms
        """
        match (self.thread_type):
            case ThreadType.SECOND.value:
                return self._last_time * 1000.0
            case ThreadType.MILLI_SECOND.value:
                return self._last_time
            case ThreadType.MICRO_SECOND.value:
                return self._last_time / 1000.0
            case ThreadType.NANO_SECOND.value:
                return self._last_time / 1000.0 / 1000.0
            case ThreadType.INSTANT.value:
                return self._last_time / 1000.0 / 1000.0
            case ThreadType.EXPONENTIAL_SECOND.value:
                return self._last_time * 1000.0
            case _:
                return self._last_time

    def get_next_update(self) -> float:
        """ returns the timestamp of the next `ObserverThread` iteration in ms
        """
        match (self.thread_type):
            case ThreadType.SECOND.value:
                return self._next_time * 1000.0
            case ThreadType.MILLI_SECOND.value:
                return self._next_time
            case ThreadType.MICRO_SECOND.value:
                return self._next_time / 1000.0
            case ThreadType.NANO_SECOND.value:
                return self._next_time / 1000.0 / 1000.0
            case ThreadType.INSTANT.value:
                return self._next_time / 1000.0 / 1000.0
            case ThreadType.EXPONENTIAL_SECOND.value:
                return self._next_time * 1000.0
            case _:
                return self._next_time
    
    def get_counts(self) -> int:
        """ returns the number of iterations of the `ObserverService` thread execution

        Returns:
            int: number of iterations
        """
        return self._counts
    