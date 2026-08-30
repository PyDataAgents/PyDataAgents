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
    ON_OFF_SECONDS = "ON_OFF_SECONDS"   # thread type based on a on-/off-phase, here the observingtime is specified as int[] array, consisting of [on_time, off_time] duration
    EXPONENTIAL_SECOND = "EXPONENTIAL_SECOND"   # interval is doubling every time, starting with 1 second by default
    DAEMON = "DAEMON"   # can be used in services with their own background thread or callbackc logic