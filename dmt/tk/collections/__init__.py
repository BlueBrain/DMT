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
Custom collection classes and methods.
"""


"""
Utilities to deal with collections.
"""

from collections.abc import Iterable
import collections
from itertools import *


def head(xs):
    """..."""
    return list(islice(xs, 1))[0]

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
        isinstance(xs, Iterable) and
        not isinstance(xs, (str, bytes)) )

def get_list(head, *tail):
    """
    Make a list from items [head, tail...]

    Arguments
    head: An element
    tail: A sequence of elements
    """
    if check(head):
        return head
    return [head] + list(tail)

from .emuset import emuset
from ..field.record import Record
