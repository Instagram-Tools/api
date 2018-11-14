"""Helper module to handle time related stuff"""
import datetime


def parse_datetime(line):
    return time_in_week(parse_datetime_prefix(str(line), '%Y-%m-%d %H:%M:%S'))


def time_in_week(dt):
    return datetime.datetime(1, 1, day=dt.isoweekday(), hour=dt.hour, minute=dt.minute, second=dt.second)


def parse_datetime_prefix(line, fmt):
    try:
        t = datetime.datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.datetime.strptime(line, fmt)
        else:
            raise
    return t


def timestamp():
    return datetime.datetime.now()


def decode_datetime(dt):
    print("%s: day: %s; hour: %s" % (dt, dt.day, dt.hour))
    if dt.day == 7 and dt.hour == 23:
        s = datetime.datetime(year=1904, month=1, day=31, hour=dt.hour,
                              minute=dt.minute, second=dt.second, microsecond=0)
    else:
        s = datetime.datetime(year=1904, month=2, day=dt.isoweekday(), hour=dt.hour,
                              minute=dt.minute, second=dt.second, microsecond=0)
    return str(s) + "Z"