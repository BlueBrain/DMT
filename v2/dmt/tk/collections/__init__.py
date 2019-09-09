"""
Custom collection classes and methods.
"""


"""
Utilities to deal with collections.
"""

import collections
from itertools import *


def take(n, xs):
    """
    Take n elements from a collection

    Parameters
    ---------------------------------------------------------------------------
    n :: int #number of items to retrieve
    xs :: iterable #...
    """
    return islice(xs, n)

def drop(n, xs):
    """
    Drop n elements from an iterable.
    """
    return islice(xs, n, None)

def step(n, xs):
    """
    Step through an iterable.
    """
    return islice(xs, None, None, n)

def check(xs):
    """
    Check xs is a collection.
    """
    return(
        isinstance(xs, collections.Iterable) and
        not isinstance(xs, (str, bytes)) )

def get_list(head, *tail):
    """
    Make a list from items [head, tail...]

    Arguments
    head: An element
    tail: A sequence of elements
    """
    return [head] + list(tail)

from .emuset import emuset
