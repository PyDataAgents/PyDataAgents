from datetime import datetime, timedelta, timezone
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
    
    @staticmethod
    def seconds_till_daytime(daytime : str = "09:00:00"):
        """ computes the number of seconds from now till the specified daytime
        <br>if the specified daytime has already passed today, it is computed for the next day from now

        Args:
            daytime (str, optional): daytime schema hh:mm:ss. Defaults to "09:00:00".

        Returns:
            int: seconds
        """
        # Parse the target time
        target_time = datetime.strptime(daytime, "%H:%M:%S").time()
        now = datetime.now()
        today_target = datetime.combine(now.date(), target_time)

        # If the target time has already passed today, move it to tomorrow
        if today_target <= now:
            today_target += timedelta(days=1)
        
        # Compute the difference in seconds
        return int((today_target - now).total_seconds())
    
    @staticmethod
    def utc_to_datetime(utc : float) -> datetime:
        """ returns the given utc timestamp in datetime

        Args:
            utc (float): in ms

        Returns:
            datetime: datetime object
        """
        dt = datetime.fromtimestamp(utc / 1000.0, tz=timezone.utc)
        return dt
    
    @staticmethod
    def datetime_to_str(dt : datetime, dformat : str = "%Y-%m-%d %H:%M:%S %Z") -> str:
        """ returns a datetime object formatted as string
        
        Args:
            dt (datetime): datetime object
            dformat (string, optional): string format. Defaults to "%Y-%m-%d %H:%M:%S %Z".

        Returns:
            str: string output
        """
        s = dt.strftime(dformat)
        return s
    
    @staticmethod
    def dt_minus(dt : datetime, weeks : float = 0, days : float = 0, hours : float = 0, minutes : float = 0, seconds : float = 0) -> datetime:
        """ returns a new datetime minus the specified timedeltas

        Args:
            dt (datetime): _description_
            weeks (int, optional): _description_. Defaults to 0.
            days (int, optional): _description_. Defaults to 0.
            hours (int, optional): _description_. Defaults to 0.
            minutes (int, optional): _description_. Defaults to 0.
            seconds (int, optional): _description_. Defaults to 0.

        Returns:
            datetime: _description_
        """
        ndt = dt - timedelta(weeks = weeks, days = days, hours = hours, minutes = minutes, seconds = seconds)
        return ndt
    
    @staticmethod
    def dt_plus(dt : datetime, weeks : float = 0, days : float = 0, hours : float = 0, minutes : float = 0, seconds : float = 0) -> datetime:
        """ returns a new datetime plus the specified timedeltas

        Args:
            dt (datetime): _description_
            weeks (int, optional): _description_. Defaults to 0.
            days (int, optional): _description_. Defaults to 0.
            hours (int, optional): _description_. Defaults to 0.
            minutes (int, optional): _description_. Defaults to 0.
            seconds (int, optional): _description_. Defaults to 0.

        Returns:
            datetime: _description_
        """
        ndt = dt + timedelta(weeks = weeks, days = days, hours = hours, minutes = minutes, seconds = seconds)
        return ndt