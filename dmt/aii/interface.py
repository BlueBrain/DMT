"""According to ZOPE:
An interface specifies the external behavior of objects that 'provide' them,
through

1. Informal documentation in a doc string
2. Attribute definitions
3. Invariants, conditions that must hold for objects that provide the interface

An object's interface specifies the object's
1. characteristics
2. behavior
3. capabilities
The interface describes what an object can do, to learn how, you must look at
the implementation.
"""

from types import FunctionType
from dmt.vtk.author import Author

class InterfaceMeta(type):
    """A metaclass to be create an Interface.
    At some point we should come around to stripping any implementation
    of required adapter methods. This will enforce a strict interface which
    does not allow any method implementations within its body."""

    def __init__(cls, name, bases, attrs):
        """..."""
        cls.__requiredmethods__ = [k for k in attrs.keys()
                                   if k not in ['__module__',
                                                '__doc__',
                                                '__qualname__']]
        cls.__interfacemethods__ = cls.__requiredmethods__
        msg = '\n' + 80 * '-' + "\n"
        msg += "{} for {} requires you to implement\n"\
               .format(name, cls.__name__)
        n = 1
        for m, mm in attrs.items():
            if not m in ['__module__', '__qualname__', '__doc__']:
                msg += "\t({}) {}: ".format(str(n), m)
                if mm.__doc__ is not None:
                    msg += mm.__doc__
                    msg += "\n" 
                    n += 1
                    msg += 80 * '-' + "\n"
        cls.__implementation_guide__ = msg
                
        super(InterfaceMeta, cls).__init__(name, bases, attrs)


class Interface(metaclass=InterfaceMeta):
    """Abstract base class to define an Interface."""
    def __init__(self, *args, **kwargs):
        """An interface cannot be initialized"""
        raise Exception("""{} is an Interface. You may not initialize an interface.
        You must implement it!""")

    __implementation_registry__ = {}

    @classmethod
    def __unimplemented(cls, impl):
        """List of methods that were not implemented by implementation 'impl'.
        We may want to check that 'impl' actually implements,
        i.e. the method is not 'abstractmethod' or is still a 'requiredmethod'.
        However we cannot check for everything!"""
        return [m for m in cls.__interfacemethods__ if not hasattr(impl, m)]

    @classmethod
    def register_implementation(cls, impl):
        """Register an implementation."""
        impl_cls = impl if isinstance(impl, type) else type(impl)

        unimpl = cls.__unimplemented(impl_cls)
        if len(unimpl) > 0:
            print("""To use {} as an implementation interface {},
            please provide: """.format(impl_cls, cls))
            n = 1
            for m in unimpl:
                print("{}: {}\n".format(n,m))
                n += 1
            print("And take a look at {}'s  implementation guide".format(cls))
            print(cls.__implementation_guide__)
            raise Exception("Unimplemented methods required by {}".format(cls))

        cls.__implementation_registry__[impl_cls] = impl_cls

    @classmethod
    def is_implemented_by(cls, impl):
        """Is this Interface implemented by Implementation 'impl'?"""
        return len(cls.__unimplemented(impl)) == 0

    @classmethod
    def extended_with(cls, other):
        """Extend this interface with methods from another interface."""
        if not issubclass(other, Interface):
            raise Exception(
                "Can only extend with another. {} is not an Interface!"\
                .format(other)
            )
        attrs = {m: getattr(cls, m) for m in cls.__interfacemethods__}
        attrs.update({m: getattr(other, m) for m in other.__interfacemethods__})
        return type(cls.__name__, (Interface, ), attrs)


def is_interface(cls):
    """Is class 'cls' an interface.
    We establish the protocol that any class derived from Interface is
    an interface."""
    return issubclass(cls, Interface)

def interfaceattribute(attr):
    """A decorator, to be used to add a class's attribute to
    it's AdapterInterface."""
    attr.__isinterfaceattribute__ = True
    return attr

def interfacemethod(method):
    """Decorator, to be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method.__isinterfacemethod__ = True
    return method

def is_interface_required_attribute(attr):
    """Specify the protocol that an attribute is required by an interface."""
    return getattr(attr, '__isinterfaceattribute__',
                   getattr(attr, '__isinterfacemethod__', False))

def is_interface_required_method(m):
    """Specify the protocol that an attribute is a method
    required by an interface. """
    return isinstance(m, FunctionType) and is_interface_required_attribute(m)

def specifies_interface(client_cls):
    """Checks if a class has specified an Interface within it's body."""
    return any([is_interface_required_attribute(getattr(client_cls, attr))
                for attr in dir(client_cls)])

def get_interface(client_cls, name=None):
    """Create an interface for a client class.

    Parameters
    ----------------------------------------------------------------------------
    client_cls :: type #the class that may have specified an Interface
    """
    if not specifies_interface(client_cls):
        return None

    required = {m: getattr(client_cls, m) for m in dir(client_cls)
                if is_interface_required_attribute(getattr(client_cls, m))}
    name = name if name is not None \
           else "{}Interface".format(client_cls.__name__)
    return type(name, (Interface,), required)

def implementation(an_interface):
    """A class decorator to declare that a class implements an interface.
    ----------------------------------------------------------------------------

    Parameters
    ----------------------------------------------------------------------------
    an_interface :: Interface #or a subclass!

    Protocol
    ----------------------------------------------------------------------------
    A class 'cls' is an interface implementation
    'if cls.__isinterfaceimplementation__  == True'
    """
    if not is_interface(an_interface):
        raise Exception("{} is not an interface".format(an_interface))

    def effective(impl_cls):
        """Effective implementation class 'impl_cls'"""
        if not isinstance(impl_cls, type):
            raise Exception(
                "'implementation' is a class decorator. {} is not a class!"\
            .format(impl_cls)
            )
        """Effective class"""
        if not hasattr(impl_cls, 'author'):
            print("WARNING!!! {} implmentation {} should attribute its author"\
                  .format(an_interface.__name__, impl_cls.__name__))
            impl_cls.author = Author.anonymous

        an_interface.register_implementation(impl_cls)
        impl_cls.__isinterfaceimplementation__ = True
        iname = an_interface.__name__
        if hasattr(impl_cls, '__implemented_interfaces__'):
            impl_cls.__implemented_interfaces__[iname] = an_interface
        else:
            impl_cls.__implemented_interfaces__ = {iname: an_interface}
        return impl_cls

    return effective

implements = implementation #just an alias

def get_implementations(an_interface):
    """all the implementations."""
    if not isinstance(an_interface, Interface):
        raise Exception("{} is not an interface.".format(an_interface))
    return an_interface.__implementation_registry__

def implementation_registry(an_interface):
    """All implementations of an Interface."""
    if not is_interface(an_interface):
        raise Exception(
            "{} is not an interface!!!".format(an_interface.__name__)
        )
    return an_interface.__implementation_registry__

def is_interface_implementation(cls):
    """Does class 'cls' implement an interface?"""
    return getattr(cls, '__isinterfaceimplementation__', False)

def implements_interface(cls, an_interface):
    """
    Does given class implement the given interface?
    ---------------------------------------------------------------------------

    Parameters
    ---------------------------------------------------------------------------
    @cls :: type # class we want to check
    @an_interface <: Interface #subclass of Interface
    ---------------------------------------------------------------------------

    Protocol
    ---------------------------------------------------------------------------
    A class 'cls' implements the interface 'an_interface'

    Return
    ---------------------------------------------------------------------------
    @type bool
    """
    return (hasattr(cls, '__implemented_interface__') and
            an_interface.__implemented_interface__ == an_interface)

def implementation_guide(an_interface):
    """Instructions on how to implement an interface"""
    if not is_interface(an_interface):
        raise Exception("{} is not an interface!!!"\
                        .format(an_interface.__name__))
    return an_interface.__implementation_guide__


def get_required_methods(cls):
    return getattr(cls, '__interfacemethods__', [])

def is_satisfied(an_interface, a_class):
    """Is interface 'an_interface' satisfied by class 'a_class'?"""
    if not is_interface(an_interface):
        raise Exception("{} is not an interface".format(an_interface))
    return an_interface.is_implemented_by(a_class)