# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Utilities for journal.
"""
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
        try:
            day = "{}-{}-{}".format(
                self.two_char(self._value.tm_year),
                self.two_char(self._value.tm_mon),
                self.two_char(self._value.tm_mday))
            second = "{}:{}:{}".format(
                self.two_char(self._value.tm_hour),
                self.two_char(self._value.tm_min),
                self.two_char(self._value.tm_sec))
            return "<{} {}>".format(day, second)
        except AttributeError:
            return str(self._value)


def timestamp(time_value=None):
    """..."""
    return Time(time_value).stamp
