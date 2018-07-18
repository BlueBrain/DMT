"""aii is Adapter, Interface, and (their) Implementations.
A validation should employ a language of the problem domain, and not be
specialized for a particular problem domain. So the validation code in a
ValidationTestCase must interface with a model through an adapter. The author
of a ValidationTestCase must mark the methods required from the Adapter with
decorators '@requiredmethod'. To use a ValidaionTestCase for a particular
model, the user must provide an adapter implmentation."""

from types import FunctionType
from abc import ABC, abstractmethod

class InterfaceMeta(type):
    """A metaclass to be used to create Interfaces!
    This metaclass will strip away any method implementation,
    thus enforcing a strict interface that is not allowed to have any
    methods with implementations in its body."""

    def __init__(meta, name, bases, attrs):
        """..."""
        def raise_not_implemented(function):
            """..."""
            def function_eff(*args, **kwargs):
                raise NotImplementedError

            function_eff.__doc__ = function.__doc__

        for m in attrs.keys():
            attrs[m] = raise_not_implemented(attrs[m])

        super(InterfaceMeta, meta).__init__(name, bases, attrs)


class Interface(metaclass=InterfaceMeta):
    """Abstract base class to define an Interface."""

    def __init__(self, *args, **kwargs):
        """An Interface cannot be instantiated."""
        raise Exception("""{} is an Interface.
        An Interface cannot be initialized.
        It must be implemented!!!""".format(self.__class__.__name__))

    __requiredmethods__ = []
    __implementation_registry__ = {}
    __implementation_guide__ = "Please provide implementation instructions."

    @classmethod
    def register_implementation(cls, impl):
        """Register an implementation."""
        for method in cls.__requiredmethods__:
            if not hasattr(cls, method):
                print(cls.__implementation_guide__)
                raise Exception(
                    "Unimplemented method '{}' required by interface "\
                    .format(cls.__name__)
                )
        cls.__implementation_registry__[impl.__name__] = impl

def requiredmethod(method):
    """To be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method.__isrequiredmethod__ = True
    return method
    
def is_interface(cls):
    """Is class 'cls' an interface.
    We establish the protocol that any class derived from Interface is
    an interface."""
    return issubclass(cls, Interface)

def is_required_method(method):
    """Specify the protocol that a method is required by an interface."""
    return (isinstance(method, FunctionType) and
            getattr(method, '__isrequiredmethod__', False))
    
def needs_interface(client_cls):
    """Specifies the protocol that a class specifies an interface.
    A class that has any method with attribute '__isrequiredmethod__' set to
    'True' will be treated as specifying an interface.
    """
    return any([is_required_method(getattr(client_cls, method))
                for method in dir(client_cls)])
                                   
def get_interface(client_cls, name='Interface'):
    """Create an interface for a client class.
    Parameters
    ----------
    @client_cls :: type #the class that needs an interface."""
    if not needs_interface(client_cls):
        return None

    required = {m: getattr(client_cls, m) for m in dir(client_cls)
                if is_required_method(getattr(client_cls, m))}
    cname = client_cls.__name__
    spec = type(name, (Interface, ), required)
    spec.__requiredmethods__ = required.keys()

    msg = "{} for {} requires you to implement\n".format(name, cname)

    n = 1
    for m, mm in required.items():
        msg += "\t({}) {}: ".format(str(n), m)
        if mm.__doc__ is not None:
            msg += mm.__doc__
        msg += "\n"
        n += 1
    spec.__implementation_guide__ = msg
    return spec

def implementation_registry(an_interface):
    """list of implementations"""
    if not is_interface(an_interface):
        raise Exception(
            "class {} is not an interface!!!".format(an_interface.__name__)
        )
    return an_interface.__implementation_registry__
            
from abc import ABCMeta, abstractmethod
class AIMeta(ABCMeta):
    """A metaclass that will add an AdapterInterface."""
    def __new__(meta, name, bases, dct):
        return super(AIMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        cls.AdapterInterface = get_interface(cls, name='AdapterInterface')

        super(AIMeta, cls).__init__(name, bases, dct)


class AdapterInterfaceBase(metaclass=AIMeta):
    """A base class for classes that will declare an adapter interface."""

    def __init__(self, *args, **kwargs):
        self._adapter = kwargs.get('model_adapter', None)

    AdapterInterface = None

    @property
    def adapter(self):
        """The adapter implementation to be used."""
        if self._adapter is None:
            raise Exception("An Adapter for {} was not set!!!"\
                            .format(self.__class__.__name__))
        return self._adapter

    @adapter.setter
    def adapter(self, value):
        """Reset the adapter."""
        self._adapter = value

    @classmethod
    def accepted_models(cls):
        """Models that this class with AdapterInterface will accept ---
        models for which at least one concrete implementation is available."""
        return set([
            model_adapted(impl)
            for impl in implementation_registry(cls.AdapterInterface).values()
            if model_adapted(impl) is not None
        ])
        

def is_interface_implementation(cls):
    """Does class 'cls' implement an interface?"""
    return getattr(cls, '__isinterfaceimplementation__', False)

def implements_interface(cls, an_interface):
    """
    Does given class implement the given interface?
    -----------------------------------------------
    Parameters
    ----------
    @cls :: type # class we want to check
    @an_interface <: Interface #subclass of Interface
    -----------------------------------------------
    Protocol
    --------
    A class 'cls' implements the interface 'an_interface'"""
    return cls.__interface__ == an_interface
    
    
def implementation_guide(an_interface):
    """Instructions on how to implement an interface"""
    if not is_interface(an_interface):
        raise Exception("{} is not an interface!!!"\
                        .format(an_interface.__name__))
    return implementation_guide(an_interface)
    

def get_required_methods(cls):
    return getattr(cls, '__requiredmethods__', [])
    
#and now the implementations
def implementation(an_interface, adapted=None):
    """"A class decorator to declare that a class implements an interface.
    We establish a protocol.
    Protocol
    --------
    A class 'cls' is an interface implementation
    if cls.__isinterfaceimplementation__ == True
    """
    if not issubclass(an_interface, Interface):
        raise Exception("{} is not an Interface".format(an_interface.__name__))

    def effective(cls):
        """Effective class"""
        an_interface.register_implementation(cls)
        cls.__isinterfaceimplementation__ = True
        cls.__interface__ = an_interface
        if adapted is not None:
            cls.__adapted__ = adapted
        return cls
    return effective

def get_implementations(an_interface):
    """all the implementations"""
    if not isinstance(an_interface, Interface):
        raise Exception("{} is not an Interface!!!"\
                        .format(an_interface.__name__))
    return an_interface.__implementation_registry__

        
def model_adapted(impl):
    """Get models implemented by an implementation.
    We assume that one implementation will adapt only one model type."""
    return getattr(impl, '__adapted__', None)

                


