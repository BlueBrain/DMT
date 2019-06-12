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
from ..tk.journal import *


class InterfaceMeta(type):
     """
     A metaclass to create Classes representing interfaces.

     Implementation Note
     -------------------
     A strict interface should not have any method implementations within its
     body.
     """

     __interface_registry__ = {}#track interfaces that have been defined

     def __init__(cls, name, bases, attrs):
          """..."""
          if len(bases) > 1:
               raise TypeError(
                    """
                    Attempt to subclass an Interface.
                    An Interface is final.
                    """)
          super().__init__(
               name, bases, attrs)
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
                                   attr_index,
                                   attr_name,
                                   getattr(
                                        attr_value,
                                        __doc__,
                                        "no documentation!")))
                    attr_index += 1

          cls.__implementation_guide__ = suggestion.formatted()

          cls.__interface_registry__[name] = cls


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
     
     __implementation_registry__ = []

     @classmethod
     def __unimplemented_methods(cls, implementation):
          """
          Methods that were not implemented by (interface) 'implementation'.
          """
          return [
               method for method in cls.__interfacemethods__
               if not hasattr(implementation, method)]
     
     @classmethod
     def register(cls, implementation):
          """
          Register an implementation of this Interface.
          """
          type_implementation =\
               implementation\
               if isinstance(implementation, type)\
                  else type(implementation)
          
          methods_unimplemented=\
               cls.__unimplemented_methods(implementation)
          
          if len(methods_unimplemented) > 0:
               suggestion =\
                    Suggestion(
                         """
                         To use {} as an implementation of Interface {},
                         please implement the following:
                         """.format(type_implementation, cls))
               n = 1
               for method in methods_unimplemented:
                    suggestion =\
                         suggestion +\
                         """
                         ({}): {}
                         """.format(n, method)
                    n += 1
                    suggestion =\
                         suggestion +\
                         """
                         Take a look at {}'s implementation guide.
                         """.format(cls)
                    suggestion =\
                         suggestion +\
                         cls.__implementation_guide__
                    raise Exception(
                         """
                         Unimplemented methods required by Interface {}.
                         """.format(cls))
               
          cls.__implementation_registry__\
             .append(type_implementation)
               
          return cls.__implementation_registry__
          
     @classmethod
     def is_implemented_by(cls, implementation):
          """
          Is this Interface implemented by 'implementation'?
          """
          return len(cls.__unimplemented_methods(implementation)) == 0


def interfacemethod(method):
     """
     Decorate method to be an interfacemethod.
     """
     if not isinstance(method, FunctionType):
          raise TypeError(
               """
               Attempt to mark {} as an interface method.
               Only function types may be marked as interface methods.
               """.format(type(method)))
     method.__isinterfacemethod__ = True
     return method

def is_interface_required(method):
     """
     Is 'method' required by an Interface?
     """
     return isinstance(method, FunctionType)\
          and getattr(method, "__isinterfacemethod__", False)

def specifies_interface(client_cls):
     """
     Check if class has a specified an Interface within it's body.
     """
     return any([
          is_interface_required(getattr(client_cls, attr))
          for attr in dir(client_cls)])


def get_interface(attributes_or_class, name=None):
     """
     Get an interface from a class's attribute dict.

     Arguments
     -----------
     attributes :: dict #that contains the attributes defined in a class body.
     name :: str #desired name of the class.
     """
     if isinstance(attributes_or_class, type):
          attributes ={
               attribute: getattr(attributes_or_class, attribute)
               for attribute in dir(attributes_or_class)}
     elif isinstance(attributes_or_class, dict):
          attributes = attributes_or_class
     else:
          raise TypeError(
               """
               Interface requested from an object of type {}.
               Interfaces can be extracted from:
               1. a class, or
               2. a dict.
               """.format(type(attributes_or_class)))

     required ={
          attr_name: attr_value
          for attr_name, attr_value in attributes.items()
          if is_interface_required(attr_value)}
     interface_name =\
          name if name.endswith("Interface") or name.endswith("interface")\
          else "{}Interface".format(name)
     return type(name, (Interface,), required)


def implements(an_interface):
     """
     Decorate a class to declare that it implements 'an_interface'.

     Arguments
     -----------
     an_interface :: Interface #or a subclass.
     """
     if not issubclass(an_interface, Interface):
          raise TypeError(
               """
               {} not an Interface
               """.format(an_interface))

     def decorated(implementing_class):
          """
          Arguments
          ----------
          implementing_class :: Class to be decorated.
          """
          an_interface.register(implementing_class)
          implementing_class.__isinterfaceimplementation__ = True
          iname = an_interface.__name__
          try:
               implementing_class.__implemented_interfaces__[iname] =\
                    an_interface
          except AttributeError:
               implementing_class.__implemented_interfaces__  ={
                    iname: an_interface}
          return implementing_class

     return decorated

def get_implementations(an_interface):
     """
     All the implementations of 'an_interface'.
     """
     try:
          return an_interface.__implementation_registry__
     except AttributeError:
          raise TypeError(
               """
               {} does not seem to be an Interface
               """.format(an_interface))
     return []

     
def is_interface_implementation(cls):
     """
     ???
     """
     return getattr(cls, "__isinterfaceimplementation__", False)

def implements_interface(cls, an_interface):
     """
     Does class 'cls' implement the Interface 'an_interface'?
     """
     try:
          return an_interface.__name__ in cls.__implemented_interfaces__
     except AttributeError:
          pass
     return False

def implementation_guide(an_interface):
     """
     Instructions on how to implement the Interface 'an_interface'.
     """
     try:
          return an_interface.__implementation_guide__
     except AttributeError:
          raise TypeError(
               """
               Cannot get implementation guide of {}.
               Is {} class an Interface?
               """.format(
                    an_interface,
                    an_interface))
     return None

def get_required_methods(cls):
     return getattr(cls, "__interfacemethods__", [])
