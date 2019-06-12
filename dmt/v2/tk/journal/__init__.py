"A logging utility"

from enum import Enum


class Level(Enum):
    """Level at which a Journal should log"""
    STUDY   = 0
    DEBUG   = 1
    DEVELOP = 2
    TEST    = 2
    INFO    = 3
    PROD    = 4


class Color(Enum):
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

from .logger import Logger
from .message import *



from ..field import\
    Field,\
    WithFields

class Timestamp(
        WithFields):
    """
    A simple record to stamp time manually.
    It's use will be to stamp source-code with Messages.
    For example developer notes can benefit from a record of the time
    they are written into the source code.
    """

    year = Field(
        """
        Year of the time stamp.
        """)
    month = Field(
        """
        Month of the time stamp.
        """)
    day = Field(
        """
        Month of the time stamp.
        """)
    hour = Field(
        """
        Hour of the time stamp, in a 24 hour clock.
        """,
        __required__=False)
    minute = Field(
        """
        Minute of the time stamp.
        """,
        __required__=False)

    @staticmethod
    def get_field(
            timestring: str,
            start: int,
            stop:int =None, 
            is_valid=lambda xyz: True):
        """
        Get field from 'timestring'
        """
        try:
            xyz = timestring[start:stop]
        except:
            return None
        return xyz if is_valid(xyz) else None

    @staticmethod
    def get_year(timestring):
        """
        Parse 'timestring' to get year.
        """
        return Timestamp.get_field(
            timestring,
            start=1,
            stop=5,
            is_valid=lambda year: len(year)==4)

    @staticmethod
    def get_month(timestring):
        """
        Parse 'timestring' to get month.
        """
        return Timestamp.get_field(
            timestring,
            start=6,
            stop=8,
            is_valid=lambda month: len(month)==2)

    @staticmethod
    def get_day(timestring):
        """
        Parse 'timestring' to get day.
        """
        return Timestamp.get_field(
            timestring,
            start=9,
            stop=11,
            is_valid=lambda day: len(day)==2)


    @staticmethod
    def get_hour(timestring):
        """
        Parse 'timestring' to get hour
        """
        return Timestamp.get_field(
            timestring,
            start=12,
            stop=14,
            is_valid=lambda hour: len(hour)==2)

    @staticmethod
    def get_minute(timestring):
        """
        Parse 'timestring' to get minute.
        """
        return Timestamp.get_field(
            timestring,
            start=15,
            stop=17,
            is_valid=lambda minute: len(minute)==2)

    @staticmethod
    def get_second(timestring):
        """
        Parse 'timestring' to get second
        """
        return Timestamp.get_field(
            timestring,
            start=18,
            stop=20,
            is_valid=lambda second: len(second)==2)

    def __init__(self,
            timestring=None,
            *args, **kwargs):
        """
        Initialize from a string.
        Format allowed: <YYYY-MM-DD HH:MM>
        """
        if timestring:
            kwargs = dict(
                year=self.get_year(timestring),
                month=self.get_month(timestring),
                day=self.get_day(timestring),
                hour=self.get_hour(timestring),
                minute=self.get_minute(timestring),
                second=self.get_second(timestring))
        return super().__init__(
            *args, **kwargs)


                 
