import time


class TimeUtils:
    
    @staticmethod
    def utc_ms():
        t = time.time()
        ts = round(t * 1000, 0)
        return ts
    
    @staticmethod
    def utc_s():
        t = time.time()
        return round(t, 0)
    
    @staticmethod
    def now_iso8601():
        """
        Returns the current time in ISO 8601 format.
        """
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"