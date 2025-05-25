import time

from PyDataGrabber.statemachine.Action import Action

class SleepAction(Action):
    """
    An action that sleeps for a specified number of seconds.
    """

    def __init__(self):
        super().__init__()
        self.sleep_time = 0

    def execute(self):
        print(f"Sleeping for {self.sleep_time} seconds")
        time.sleep(self.sleep_time)
        print("Sleep action completed")