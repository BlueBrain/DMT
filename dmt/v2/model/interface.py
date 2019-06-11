"""
An interface specifies the external behavior of objects that 'provide' them,
through
1. Informal documentation in a doc string
2. Attribute definitions
3. Invariants, conditions that must hold for objects that provide the interface

An object's interface specifies the object's
1. characteristics
2. behavior
3. capabilities

The interface describes what an object can do.
To learn how, you must look at the implementation.
"""

from types import FunctionType
from ..tk.author import Author
from ..tk.journal.message import Suggestion


class InterfaceMeta(type):
     """
     A metaclass to create Classes representing interfaces.

     Implementation Note
     -------------------
     A strict interface should not have any method implementations within its
     body.
     """
     def __init__(cls, name, bases, attrs):
         """..."""
         cls.logger =\
             Logger(cls.__name__)
         python_provided_attributes={
             "__module__",
             "__doc__",
             "__qualname__"}
         cls.__requiredmethods__ =[
             attr_name for attr_name in attrs.keys()
             if attr_name not in python_provided_attributes]
         cls.__interfacemethods__ =\
             cls.__requiredmethods__
         suggestion =\
             Suggestion(
                 """
                 {} for {} requires you to implement.
                 """.format(name, cls.__name__))
         attr_index = 1
         for attr_name, attr_value in attrs.items():
             if attr_name not in python_provided_attributes:
                 suggestion =\
                     suggestion +\
                     Suggestion(
                         "\t({}) {}: {}".format(
                              str(attr_index),
                              attr_name,
                              getattr(attr_value, __doc__, "no documentation!"))
                 attr_index += 1

        cls.__implementation_guide__ = suggestion.formatted

        super().__init__(
            name, bases, attrs)


class Interface(
        metaclass=InterfaceMeta):
    """
    Abstract base class to define an Interface
    """

    def __init__(self,
            *args, **kwargs):
        """An Interface cannot be initialized."""
        raise Exception(
            """
            Initialization of {}, which is an Interface.
            An Interface may not be initialized
            """.format(self.__class__.__name__))
                 





