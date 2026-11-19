import time
from threading import Timer, Event
from enum import Enum

from pydag.services.iolink.sensors.VVB301.base_command import BaseCommand


# calls a command repetitively: either on a timer basis until the user quits
# or for a certain number of times until we reach a certain number of samples


class RepetitiveCommand(BaseCommand):
    """
        class RepetitiveCommand
        ===========
        Specialized command which executes the same command repetitievely.

        This is done either based on a wait interval from the last execution or a certain number of times without any waiting in between.
        This is determined by the combination of its input values given at construction
        Because of its indefinite execution nature, this command can be aborted by the user and has a state transition which can be
        inspected by attaching a listener function. When constructed it is deemed as *NotStarted*. If execute was called and
        its in the *NotStarted* state it will begin execution and transition to *Started*. From *Started* it can 
        be *Aborted* by the user or once  it has finished runnning for specified number of times if will be set to *Finished*.
    """
    

    class State(Enum):
        NotStarted = 0
        Started = 1
        Aborted = 2
        Finished = 3

    def __init__(self, url, request_data, number_samples=1, interval_time_ms=0):
        super().__init__(url, "",request_data)
        self._number_samples = number_samples
        self._request_repeat_time_ms = interval_time_ms
        if self._number_samples < 1 and self._request_repeat_time_ms < 1:
            # invalid combination, given default to a one time call
            self._number_samples = 1
        if self._number_samples > 0:
            #invalidate the timer
            self._request_repeat_time_ms = 0
        self._abort = Event()
        self.state_function = lambda x: x
        self._internal_state = RepetitiveCommand.State.NotStarted

    def register_state_listener(self, on_state_changed):
        self.state_function = on_state_changed
    
    def execute(self):
        if self._internal_state is RepetitiveCommand.State.Aborted:
            return None
        self._internal_state =  RepetitiveCommand.State.Started
        self.state_function(self._internal_state)
        if self._number_samples > 0:
            self._execute_till_number_samples_received()
        elif self._request_repeat_time_ms > 0:
            self._execute_at_interval()
        #emit finished state if it wasn't aborted,
        if self._internal_state is RepetitiveCommand.State.Started:
            self._internal_state =  RepetitiveCommand.State.Finished
            self.state_function(self._internal_state)

    def _execute_till_number_samples_received(self):
        assert(self._number_samples > 0)
        for _ in range(self._number_samples):
            if self._abort.is_set():
                return
            else:
                #might need to add a delay !? in case its too frequent
                super().execute()
    
    def _execute_at_interval(self):
        def repeat_execute_at_intervals():
            if not self._abort.is_set():
                super(RepetitiveCommand,self).execute()
                Timer(self._request_repeat_time_ms / 1000, repeat_execute_at_intervals).start()
        repeat_execute_at_intervals()
        #wait on this thread (since the timer thread will be different) until abort is called
        self._abort.wait()

    def abort_execution(self):
        self._abort.set()
        self._internal_state = RepetitiveCommand.State.Aborted
        self.state_function(self._internal_state)
    
    #resets the state to not started if aborted or finished to allow it to be re-run
    def reset_state(self):
        if self._internal_state is RepetitiveCommand.State.Aborted:
            self._abort.clear()
        if self._internal_state is RepetitiveCommand.State.Aborted or self._internal_state is RepetitiveCommand.State.Finished:
            self._internal_state = RepetitiveCommand.State.NotStarted