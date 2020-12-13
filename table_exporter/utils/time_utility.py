# coding=utf-8
import time
import calendar
import datetime


class MyTZInfo(datetime.tzinfo):
    """
    自定义时区信息
    如果需要更加复杂的时区和夏令时信息，可以考虑引入pytz库
    """

    def __init__(self, my_tz, my_dst, my_name):
        """
        :param my_tz: 时区，小时
        :param my_dst: 夏令时修正，小时
        :param my_name: 自定义时区名称
        """
        super(MyTZInfo, self).__init__()
        self.my_tz = my_tz
        self.my_dst = my_dst
        self.my_name = my_name

        self.utc_offset_seconds = self.utcoffset(0).total_seconds()

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.my_tz) + self.dst(dt)

    def dst(self, dt):
        return datetime.timedelta(hours=self.my_dst)

    def tzname(self, dt):
        return self.my_name


# 默认北京时间
time_zone = MyTZInfo(+8, 0, "UTC8")


def get_local_time(timestamp):
    if timestamp is None:
        timestamp = time.time()
    local_timestamp = timestamp + time_zone.utc_offset_seconds
    return time.gmtime(local_timestamp)


def date_str2timestamp(date_str, fmt):
    dt = datetime.datetime.strptime(date_str, fmt)
    return calendar.timegm(dt.replace(tzinfo=time_zone).utctimetuple())


def timestamp2date_str(timestamp, fmt):
    return time.strftime(fmt, get_local_time(timestamp))
