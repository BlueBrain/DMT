"""
Another None.
"""

from .singleton import Singleton

class NullType(Singleton):
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


NA = NullType()
