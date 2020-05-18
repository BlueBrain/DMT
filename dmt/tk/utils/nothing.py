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
Another None.
"""

from collections.abc import Mapping
from .singleton import Singleton

class NullType(Singleton, Mapping):
    """
    ...
    """
    def __nonzero__(self):
        """
        Python 2 uses this.
        """
        return False

    def __bool__(self):
        """
        Python 3.
        """
        return False

    def __str__(self):
        """..."""
        return "<<<Not Available>>>"

    def __repr__(self):
        """..."""
        return self.__str__()

    def __iter__(self):
        """
        Make `NullType` iterable.
        Then it can be used to default an argument to not available/applicable
        (NA) iterable.
        """
        return self

    def __next__(self):
        """
        A NullType contains nothing.
        """
        raise StopIteration

    def __getitem__(self, item):
        raise KeyError(
            """
            Null Type NA cannot contain any item.
            """)

    def __len__(self):
        return 0

    def __contains__(self, x):
        """
        A null-type should not contain anything.
        """
        return False


NA = NullType()
