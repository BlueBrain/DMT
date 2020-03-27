# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Property is a subtype of Field.
"""
import collections
from ..collections import emuset
from ..field import Field


class Property(Field):
    """
    Fully define a property of an object,
    specifying the key to be used to index data-sets containing
    the object, as well as its value type, and the set of values it may assume.
    """
    def __init__(self,
            __label__=None,
            __type__=object,
            __value_set__=set(),#empty means any value
            *args, **kwargs):
        """
        Initialize...
        """
        def __is_valid(instance, value):
            """
            Validate a value.

            Arguments
            -------------
            value :: Either a singleton, or an iterable.
            If 'value' is a singleton, it should be of the accepted type.
            If 'value' is an iterable (for e.g. a set of values), each
            of these values must be of the accepted type.
            """
            value_is_collection =\
                isinstance(value, collections.Iterable) and\
                not isinstance(value, (str, bytes))
            if __value_set__:
                if value_is_collection:
                    return all(
                        isinstance(v, __type__) and v in __value_set__
                        for v in value)
                return isinstance(value, __type__) and value in __value_set__
            if value_is_collection:
                return all(
                    isinstance(v, __type__)
                    for v in value)
            return isinstance(value, __type__)

        if __value_set__:
            self.__value_set__= emuset(*__value_set__)
        super().__init__(
            __validation__=__is_valid,
            *args, **kwargs)
