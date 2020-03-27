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
Field at the class level.
"""

import functools
from .field import Field

def shout(error):
    raise error


class ClassField:
    """
    A field attached to the class itself, not its instances.
    """
    def __init__(self,
            __doc__,
            **kwargs):
        """
        Initialize Me.
        """
        if len(kwargs) != 1:
            raise TypeError(
                """
                __init__() missing 1 required key-value pair (
                i.e. a single element variable keyword argument sequence).
                """)
        self.__doc__ = __doc__
        self.__attr_name__ , self.__value__ = tuple(kwargs.items())[0]

    def __set__(self, instance, value):
        """..."""
        raise TypeError(
            """
            Cannot change value of ClassField
            """)

    def __get__(self, instance, owner):
        """..."""
        try:
            class_field_docs = owner.__doc_for_field__
        except AttributeError:
            owner.__doc_for_field__ = {}
        finally:
            class_field_docs = owner.__doc_for_field__

        if self not in class_field_docs:
            class_field_docs[self.__attr_name__] = self.__doc__
        
        return self.__value__


def class_field(method):
    """
    Decorate a class method to make it behave like a `ClassField` instance.
    """
    try:
        class_field_has_been_set = method.__has_been_set__
    except AttributeError:
        method.__has_been_set__ = False
    finally:
        class_field_has_been_set = method.__has_been_set__

    class_field_instance = ClassField(
        method.__doc__,
        **{method.__name__: method(None)})

    @functools.wraps(method)
    def effective(instance_or_class):
        if not method.__has_been_set__:
            try:
                setattr(
                    instance_or_class.__class__,
                    method.__name__,
                    class_field_instance)
            except TypeError:
                setattr(
                    instance_or_class,
                    method.__name__,
                    class_field_instance)
            method.__has_been_set__ = True
        else:
            print("{} already set.".format(method.__name__))

    return effective
