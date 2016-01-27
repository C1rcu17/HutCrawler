from datetime import datetime, timedelta


__TIMEZONE = None


def get_tz(tz=None):
    from pytz import timezone
    from tzlocal import get_localzone
    return __TIMEZONE if tz is None else get_localzone() if tz == 'unix' else timezone(tz)


def set_tz(tz=None):
    global __TIMEZONE
    __TIMEZONE = get_tz(tz)


def localize(date, tz=None):
    return date.replace(tzinfo=get_tz(tz))


def now(tz=None):
    return localize(datetime.now(), tz)


def parse(string, frmt, tz=None):
    return localize(datetime.strptime(string, frmt), tz)


def sub(date, *args, **kwargs):
    return date - timedelta(*args, **kwargs)


def add(date, *args, **kwargs):
    return date + timedelta(*args, **kwargs)


def dup(date):
    return date.replace()


def f(date, frmt=None):
    return date.isoformat(sep=' ') if frmt is None else date.strftime(frmt)


def dump(date, frmt=None):
    print(f(date, frmt))
