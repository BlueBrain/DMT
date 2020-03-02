"""
Nothing like None
"""

from .singleton import Singleton

class NullType(Singleton):
    """
    Null may be 'Not-Available', or 'Not-Applicable`.
    """
    def __nonzero__(self):
        """
        Used by Python 2
        """
        return False

    def __bool__(self):
        """
        Used by Python 3
        """
        return False


NA = NullType()
