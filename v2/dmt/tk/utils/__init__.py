"""
Little useful methods.
"""
from .string_utils import *
import time
from collections import namedtuple

def get_label(something):
    """
    Get a label for some object
    """
    try:
        return something.label
    except AttributeError:
        try:
            return something.get_label()
        except AttributeError:
            try:
                return something["label"]
            except KeyError:
                return "unavailable"
            except TypeError:
                pass
    return str(something)


class NothingType:
    """
    Another kind of None.
    This should be a singleton.
    """
    def __nonzero__(self):
        """
        Used to evaluate bool values in Python 2
        Nothing is not true.
        """
        return False

    def __bool__(self):
        """
        Used to evaluate bool values in Python 2
        Nothing is not true.
        """
        return False


Nothing = NothingType()

DayTime = namedtuple("DayTime", ["day", "time"])

def timestamp(now=None, sep=None):
    """stamp for saving..."""
    def two_char(s):
        """Make string 's' at least two characters long."""
        s = str(s)
        return s if len(s) >= 2 else ("0{}".format(s) if len(s) == 1 else "00")
    now = now if now else time.localtime()
    ts = DayTime(
        day="{}{}{}".format(
            two_char(now.tm_year),
            two_char(now.tm_mon),
            two_char(now.tm_mday)),
        time="{}{}{}".format(
            two_char(now.tm_hour),
            two_char(now.tm_min),
            two_char(now.tm_sec)) )
    return "{}{}{}".format(ts.day, sep, ts.time) if sep else ts


