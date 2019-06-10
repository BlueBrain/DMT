"""
Class attribute with description
"""

import sys
import collections
from .field import Field

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
        self.__default_value__ = __default_value__

    @property
    def description(self):
        """Describe this ClassAttribute"""
        return "ClassAttribute<{}>".format(self.__doc__)

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
