from datetime import datetime
import time
from loguru import logger

from pydag.services.Observer import Observer
from pydag.services.ObserverService import ObserverService
from pydag.services.ObserverThread import ObserverThread
from pydag.services.Service import Service
from pydag.services.ThreadType import ThreadType
from pydag.utils.TimeUtils import TimeUtils

def test_second_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=1, thread_type=ThreadType.SECOND.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(5)
    ot.terminate()

def test_millisecond_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=100, thread_type=ThreadType.MILLI_SECOND.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(1)
    ot.terminate()

def test_microsecond_thread():
    service = TestService()
    t_obs = 1000 # µs
    t_sleep = 0.02 # s
    ot = ObserverThread(service=service, observing_time=t_obs, thread_type=ThreadType.MICRO_SECOND.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(t_sleep)
    ot.terminate()
    print(f"counts: {ot.get_counts()}")
    assert ot.get_counts() >= t_sleep * 1000000.0 / t_obs - 1

def test_nanosecond_thread():
    service = TestService()
    t_obs = 1000000 # ns
    t_sleep = 0.01 # s
    ot = ObserverThread(service=service, observing_time=t_obs, thread_type=ThreadType.NANO_SECOND.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(t_sleep)    
    ot.terminate()
    print(f"counts: {ot.get_counts()}")
    assert ot.get_counts() >= t_sleep * 1000000000.0 / t_obs - 1

def test_instant_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=0, thread_type=ThreadType.INSTANT.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(0.1)
    ot.terminate()

def test_only_once_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=None, thread_type=ThreadType.ONLY_ONCE.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    ot.terminate()

def test_daytime_thread():
    wt : int = 5
    dt : datetime = TimeUtils.dt_plus(datetime.now(), seconds=wt)
    ot : str = dt.strftime("%H:%M:%S")
    service = TestService()
    ot : ObserverThread = ObserverThread(service=service, observing_time=ot, thread_type=ThreadType.DAYTIME.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(2 * wt)
    ot.terminate()

def test_datetime_thread():
    wt : int = 5
    service = TestService()
    dts : str = TimeUtils.dt_plus(datetime.now(), seconds=wt).strftime("%Y-%m-%d %H:%M:%S")
    ot = ObserverThread(service=service, observing_time=dts, thread_type=ThreadType.DATETIME.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()
    time.sleep(2 * wt)
    ot.terminate()

def test_triggered_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=None, thread_type=ThreadType.TRIGGERED.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()    
    ot.notify_observers()     
    ot.terminate()
    
def test_exponential_thread():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=1, thread_type=ThreadType.EXPONENTIAL_SECOND.value)
    o = TestObserver()
    ot.add_observer(o)
    ot.run()    
    time.sleep(32)    
    ot.terminate()
    
def test_second_thread_next_time():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=2, thread_type=ThreadType.SECOND.value)
    o = TestObserver2(ot)
    ot.add_observer(o)
    ot.run()
    time.sleep(5)
    ot.terminate()
    
def test_millisecond_thread_next_time():
    service = TestService()
    ot = ObserverThread(service=service, observing_time=500, thread_type=ThreadType.MILLI_SECOND.value)
    o = TestObserver2(ot)
    ot.add_observer(o)
    ot.run()
    time.sleep(2)
    ot.terminate()

class TestObserver(Observer):
    def observe(self):
        logger.info("observing...")
    
    def unobserve(self):
        logger.info("unobserving...")

class TestObserver2(Observer):
    
    def __init__(self, othread : ObserverThread):
        super().__init__()
        self._othread : ObserverThread = othread
    
    def observe(self):
        logger.info(f"last: {self._othread.get_last_update()} -> next: {self._othread.get_next_update()}")
    
    def unobserve(self):
        logger.info("unobserving...") 
        
class TestService(Service):    
    
    def _on_install(self, agent = None):
        return
    
    def _on_start(self):
        return 
    
    def _on_stop(self):
        return
    
    def _on_uninstall(self, agent = None):
        return
