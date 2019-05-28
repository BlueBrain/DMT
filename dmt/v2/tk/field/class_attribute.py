"""
Class attribute with description
"""

import sys
import collections
from .field import Field

class ClassAttribute(Field):
    """
    ClassAttribute of a class is defined on the class itself, not an instance.
    """
    def __init__(self,
            __value__,
            __doc__:str):
        """Initialize Me
        Arguments:
        ~   __doc__ :: A string describing this ClassAttribute
        ~   __value__ :: The (initial) value for this class attribute
        """
        self.__doc__ = __doc__
        self.__value__ = __value__
        self.__number_retrieval__ = 0

    def __set__(self, instance, value):
        """Value of a class attribute cannot be set on a class instance."""
        raise Exception(
            "Setting a class attribute of an instance.")

    @property
    def description(self):
        """Describe this ClassAttribute"""
        return "ClassAttribute<{}>".format(self.__doc__)

    def __get__(self, instance, owner):
        """The effective value of this class attribute."""
        #print("get class attribute with {} retrievals".format(self.__number_retrieval__))
        self.__number_retrieval__ += 1
        if self.__number_retrieval__ <= 2:
            return self
        setattr(owner, self.__attr_name__, self.__value__)
        return self.__value__
