from datetime import datetime
import time
from loguru import logger

from pydag.services.Observer import Observer
from pydag.services.ObserverService import ObserverService
from pydag.services.ThreadType import ThreadType
from pydag.utils.TimeUtils import TimeUtils

def test_second_thread():
    s = TestService(observing_time=1, thread_type=ThreadType.SECOND.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(5)
    s.stop()

def test_millisecond_thread():
    s = TestService(observing_time=100, thread_type=ThreadType.MILLI_SECOND.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(1)
    s.stop()

def test_microsecond_thread():
    t_obs = 10000 # µs
    t_sleep = 0.05 # s
    s = TestService(observing_time=t_obs, thread_type=ThreadType.MICRO_SECOND.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(t_sleep)
    s.stop()
    print(f"counts: {s.get_counts()}")
    assert s.get_counts() >= t_sleep * 1000000.0 / t_obs - 1

def test_nanosecond_thread():
    t_obs = 1000000 # ns
    t_sleep = 0.01 # s
    s = TestService(observing_time=t_obs, thread_type=ThreadType.NANO_SECOND.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(t_sleep)    
    s.stop()
    print(f"counts: {s.get_counts()}")
    assert s.get_counts() >= t_sleep * 1000000000.0 / t_obs - 1

def test_instant_thread():
    s = TestService(observing_time=0, thread_type=ThreadType.INSTANT.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(0.1)
    s.stop()

def test_only_once_thread():
    s = TestService(observing_time=None, thread_type=ThreadType.ONLY_ONCE.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()

def test_daytime_thread():
    wt : int = 5
    dt : datetime = TimeUtils.dt_plus(datetime.now(), seconds=wt)
    ot : str = dt.strftime("%H:%M:%S")
    s = TestService(observing_time=ot, thread_type=ThreadType.DAYTIME.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(2 * wt)
    s.stop()

def test_datetime_thread():
    wt : int = 5
    dts : str = TimeUtils.dt_plus(datetime.now(), seconds=wt).strftime("%Y-%m-%d %H:%M:%S")
    s = TestService(observing_time=dts, thread_type=ThreadType.DATETIME.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(2 * wt)
    s.stop()

def test_triggered_thread():
    s = TestService(observing_time=None, thread_type=ThreadType.TRIGGERED.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()    
    s.notify_observers()     
    s.stop()
    
def test_exponential_thread():
    s = TestService(observing_time=1, thread_type=ThreadType.EXPONENTIAL_SECOND.value)
    o = TestObserver()
    s.add_observer(o)
    s.install()
    s.start()    
    time.sleep(32)    
    s.stop()
    
def test_second_thread_next_time():
    s = TestService(observing_time=2, thread_type=ThreadType.SECOND.value)
    o = TestObserver2(s)
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(5)
    s.stop()
    
def test_millisecond_thread_next_time():
    s = TestService(observing_time=500, thread_type=ThreadType.MILLI_SECOND.value)
    o = TestObserver2(s)
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(2)
    s.stop()
    
def test_on_off_second_thread():
    s = TestService(observing_time=[10, 20], thread_type=ThreadType.ON_OFF_SECONDS.value)
    o = TestObserver2(s)
    s.add_observer(o)
    s.install()
    s.start()
    time.sleep(150)
    s.stop()

class TestObserver(Observer):
    def observe(self):
        logger.info("observing...")
    
    def unobserve(self):
        logger.info("unobserving...")

class TestObserver2(Observer):
    
    def __init__(self, oservice : ObserverService):
        super().__init__()
        self.oservice : ObserverService = oservice
    
    def observe(self):
        logger.info(f"last: {self.oservice.get_last_update()} -> next: {self.oservice.get_next_update()}")
    
    def unobserve(self):
        logger.info("unobserving...") 
        
class TestService(ObserverService):
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
    
    def _on_start(self):
        super()._on_start() 
    
    def _on_stop(self):
        super()._on_stop()
    
    def _on_uninstall(self, agent = None):
        super()._on_uninstall(self)
