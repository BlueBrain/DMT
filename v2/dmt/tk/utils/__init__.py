"""
Little useful methods.
"""
from .string_utils import *


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
