import pytz
from web_app import settings
from datetime import datetime as _datetime
from pytz import timezone

TZ = None

if settings.USE_TZ:
    if not settings.TIME_ZONE:
        TZ = pytz.utc

    TZ = settings.TIME_ZONE


class TimeZone(object):
    """
    We need timezones in order to accurately timestamp
    information stored in the database
    """
    def __init__(self, tz):
        self.tz = timezone(tz)

    def get_datetime(self):
        """
        get datetime object with timezone enabled
        :return:
        """
        _dt = _datetime.now(tz=self.tz)
        return _dt

datetime = TimeZone(TZ).get_datetime()
