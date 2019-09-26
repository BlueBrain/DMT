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
