"""Journal utilities"""
import time

class Time:
    """Customized Time"""

    def __init__(self, now=None):
        """Initialize Me"""
        self._value = now if now else time.localtime()


    @staticmethod
    def two_char(s):
        """Make string of 's' at least two char long"""
        s = str(s)
        return s if len(s) >= 2 else\
            ("0{}".format(s) if len(s) == 1 else "00")

    @property
    def stamp(self):
        """Stamp for this time value"""
        day = "{}-{}-{}".format(
            self.two_char(self._value.tm_year),
            self.two_char(self._value.tm_mon),
            self.two_char(self._value.tm_mday))
        second = "{}:{}:{}".format(
            self.two_char(self._value.tm_hour),
            self.two_char(self._value.tm_min),
            self.two_char(self._value.tm_sec))
        return "<{} {}>".format(day, second)


def timestamp(time_value=None):
    """..."""
    return Time(time_value).stamp
