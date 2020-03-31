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
Field with description
"""
import sys
import copy
import collections

class Field:
    """
    Field of a class, with description
    """

    __is_field__ = True

    def __init__(self,
            __doc__: str,#documentation for this Field is required
            __type__=object,
            __validation__=lambda x: True,
            __required__=True,
            __default_value__=None,
            __as__=lambda obj: obj,
            __examples__=[]):
        """Initialize Me"""
        self.__doc__ = __doc__
        self.__type__ = __type__
        self.__validation__ = __validation__
        self.__required__ = __required__
        self.__attr_name__ = None
        self._default_value = __default_value__
        self._cast = __as__
        self.__examples__  = __examples__
        self.__defined_in__ = "Unknown"

    def _get_instance_attribute_name(self, instance):
        """
        The attribute name that an instance of a class with
        this Field instance will store its value with.
        """
        self._check_name()
        type_prefix =\
            self.__type__.__name__ if not isinstance(self.__type__, tuple)\
            else '_'.join(t.__name__ for t in self.__type__)
        return "${}_{}".format(type_prefix, self.__attr_name__)

    def _check_name(self):
        """
        Has this Field instance been given a name?
        The intended use of Field is through the associated
        WithFields baseclass. Fields are initialized, and given a name in the
        initializer method of WithFields. So if a Field instance does not have
        a name, it could mean that the class where this Field has been defined
        does not derive from WithFields.
        """
        if self.__attr_name__ is None:
            raise AttributeError(
                """
                Field instance does not have a name (__attr_name__).
                Check if the containing class was based on WithFields.
                Field documentation:
                """.format(self.__doc__))

    def assert_validity(self, value):
        """Is 'value' valid value of this Field?"""
        if not isinstance(value, self.__type__):
            raise TypeError(
                "Cannot set field '{}' of type '{}' to value '{}' of type '{}'"\
                .format(
                    self.__attr_name__,
                    self.__type__.__name__,
                    value,
                    str(type(value))))
        if not self.__validation__(value):
            raise ValueError(
                "Field '{}' of type '{}' cannot be an invalid value."\
                .format(
                    self.__attr_name__,
                    self.__type__.__name__,
                    value))
        return True

    def cast(self, value):
        """..."""
        return value\
            if isinstance(self._cast, type) and isinstance(value, self._cast)\
               else self._cast(value)

    @property
    def default_value(self):
        """
        Get default value.
        """
        return self._cast(copy.deepcopy(self._default_value))

    @property
    def description(self):
        """Describe this Field"""
        return "Field<{}>".format(self.__doc__)

    def set_defining_class(self, cls):
        """
        Where was this `Field` defined.
        """
        self.__defined_in__ = cls.__name__

    @property
    def examples(self):
        """
        Get examples
        """
        return self.__examples__

    @property
    def documentation(self):
        """
        Documentation with examples.
        """
        if not self.__examples__:
            return self.__doc__
        return self.__doc__ + """
        You may look at some examples: `{}.{}.examples`
        """.format(
            self.__defined_in__,
            self.__attr_name__)

    def __set__(self, instance, value):
        """
        Set the value of this Field in an class instance.
        """
        self.assert_validity(value)
        setattr(instance, self._get_instance_attribute_name(instance), value)

    def __get__(self, instance, owner):
        """
        Get the value of this Field stored in an instance of the class that
        has this Field.
        """
        if instance:
            return getattr(
                instance,
                self._get_instance_attribute_name(instance))
        #assuming owner is the class in which this Field was defined...
        return self


class _from_self:
    """
    Create a field instance from an instance WithFields.
    """
    def __init__(self, function):
        if isinstance(function, _from_self):
            self.initializer = function.initializer
        self.initializer = function
        
    def __call__(self, instance, owner=None, *args, **kwargs):
        return self.initializer(instance, *args, **kwargs)


class LambdaField(Field):
    """
    A lazy field that must be provided a lambda over self as its value.
    """
    def __init__(self, __doc__, value):
        super().__init__(__doc__, __default_value__=value)
        
    def __set__(self, instance, value):
        if callable(value):
            super().__set__(instance, _from_self(value))
        else:
            super().__set__(instance, value)
        
    def __get__(self, instance, owner):
        if not instance:
            return self
        instance_attr = super().__get__(instance, owner)
        try:
            return instance_attr(instance, owner)
        except TypeError:
            return instance_attr
  
