import enum


class ThreadType(str, enum.Enum):
    MILLI_SECOND = "MILLI_SECOND"
    MICRO_SECOND = "MICRO_SECOND"
    NANO_SECOND = "NANO_SECOND"
    INSTANT = "INSTANT"
    SECOND = "SECOND"
    ONLY_ONCE = "ONLY_ONCE"
    TRIGGERED = "TRIGGERED"
    DATETIME = "DATETIME"
    DAYTIME = "DAYTIME"
    EXPONENTIAL_SECOND = "EXPONENTIAL_SECOND"   # interval is doubling every time, starting with 1 second by default
    DAEMON = "DAEMON"   # a thread that runs in the background and is not started or stopped by the ObserverThread, but by the service itself, e.g. for libraries with their own callback logic