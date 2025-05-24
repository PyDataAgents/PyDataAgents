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