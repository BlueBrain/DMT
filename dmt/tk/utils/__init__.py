# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Little useful methods.
"""
from collections import namedtuple
import time

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

#from .nothing import NA


class NullType:
    """
    Another kind of None.

    """

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

def get_file_name_base(
        file_name=None):
    """Get the base from a file name, stripping away it's suffix."""
    if file_name is None:
        return "report"
    fname_parts = file_name.split('.')
    if len(fname_parts) == 1:
        return fname_parts[0].strip().replace(' ', '_')
    return '_'.join(fname_parts[0:-1]).strip().replace(' ', '_')


