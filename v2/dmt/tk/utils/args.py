"""
Utilities to handle arguments.
"""
import functools

def require_only_one_of(**kwargs):
    """
    Require only one argument among a sequence.
    """
    assert kwargs, "Nothing passed."
    assert sum(value is not None for value in kwargs.values()) == 1,\
        "Expected one and only one argument among: {}"\
        .format([key for key in kwargs.keys()])




