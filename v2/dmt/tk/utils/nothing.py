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
        return "Not Available"

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
        return None

    def __len__(self):
        return 0


NA = NullType()
