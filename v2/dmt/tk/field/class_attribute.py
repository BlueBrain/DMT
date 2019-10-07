"""
Class attribute with description
"""

import sys
import collections
from .field import Field


class UndefinedClassAttribute(TypeError):
    """
    Exception to be raised when a (sub)-class does not implement a
    ClassAttribute. This exception will be called when the expected
    behavior from a class-attribute is invoked.
    """
    def __init__(self, key, *args):
        self.message = key
        super().__init__(key, *args)


class ClassAttribute:
    """
    ClassAttribute of a class is defined on the class itself, not an instance.
    """
    def __init__(self,
            __doc__,
            __type__=object,
            __required__=True,
            __validation__=lambda value: True,
            __default_value__=None):
        """Initialize Me
        Arguments:
        ~   __doc__ :: A string describing this ClassAttribute
        ~   __value__ :: The (initial) value for this class attribute
        """
        self.__doc__ = __doc__
        self.__type__ = __type__
        self.__number_retrieval__ = 0
        self.__required__ = __required__
        self.__validation__ = __validation__
        self._default_value = __default_value__

    @property
    def description(self):
        """Describe this ClassAttribute"""
        return "ClassAttribute<{}>".format(self.__doc__)

    def set_defining_class(self, cls):
        """
        Where was this `Field` defined.
        """
        self.__defined_in__ = cls.__name__

    @property
    def default_value(self):
        """
        Get default value.
        """
        return copy.deepcopy(self._default_value)

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
