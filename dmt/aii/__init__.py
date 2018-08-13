"""aii is Adapter, Interface, and (their) Implementations.
A validation should employ a language of the problem domain, and not be
specialized for a particular problem domain. So the validation code in a
ValidationTestCase must interface with a model through an adapter. The author
of a ValidationTestCase must mark the methods required from the Adapter with
decorators '@requiredmethod'. To use a ValidaionTestCase for a particular
model, the user must provide an adapter implmentation."""

from types import FunctionType
from abc import ABC, abstractmethod
from dmt.vtk.author import Author

class Callable(ABC):
    """A simple extension of ABC,
    with an init method that takes *args and **kwargs,
    but only to ignore them.
    This is required because abc.ABC.__init__ does not take any parameters"""
    def __init__(self, *args, **kwargs):
        """init"""
        super(Callable, self).__init__() #or don't do anything
    
class InterfaceMeta(type):
    """A metaclass to be used to create Interfaces!
    At some point we should come around to stripping any implementation
    of required adapter methods.thus enforcing a strict interface that is not 
    allowed to have any methods with implementations in its body."""
    def __init__(cls, name, bases, attrs):
        """..."""
        cls.__requiredmethods__ = [k for k in attrs.keys()
                                   if (k != '__module__' and
                                       k != '__doc__' and
                                       k != '__qualname__')]
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
        """An Interface cannot be instantiated."""
        raise Exception("""{} is an Interface.
        An Interface cannot be initialized.
        It must be implemented!!!""".format(self.__class__.__name__))

    __implementation_registry__ = {}

    @classmethod
    def register_implementation(cls, impl):
        """Register an implementation."""
        impl_cls = impl if isinstance(impl, type) else type(impl)

        unimplemented = cls.__unimplemented(impl_cls)
        if len(unimplemented) > 0:
            print("""To use {} as an implementation of {}'s adapter,
            please provide: """.format(impl_cls, cls))
            n = 1
            for method in cls.__unimplemented(impl_cls):
                print("{}: {}\n".format(n, method))
                n += 1
            print(cls.__implementation_guide__)
            raise Exception(
                "Unimplemented methods required by {}'s adapter interface"\
                .format(cls)
            )
        cls.__implementation_registry__[impl_cls] = impl_cls

    @classmethod
    def __unimplemented(cls, impl):
        """A list of methods that were not implemented by implementation
        'impl'. We may want to check that 'impl' actually implements,
        i.e. the method is not abstractmethod or still requiredmethod. However
        we cannot check for everything."""
        return [method for method in cls.__requiredmethods__
                if not hasattr(impl, method)]

    @classmethod
    def is_implemented_by(cls, impl):
        """Is this interface implemented by an implementation?
        """
        return len(cls.__unimplemented(impl)) == 0

    @classmethod
    def extended_with(cls, other):
        """Extend this interface with methods from other interface."""
        if not issubclass(other, Interface):
            raise Exception("{} is not an interface!".format(other))
        all_required_methods = {m: getattr(cls, m)
                                for m in cls.__requiredmethods__}
        for m in other.__requiredmethods__:
            all_required_methods[m] = getattr(other, m)

        return type(cls.__name__, (Interface, ), all_required_methods)


def requiredmethod(method):
    """Decorator, to be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method.__isrequiredmethod__ = True
    return method

def adaptermethod(method):
    """Decorator, to be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method.__isadaptermethod__  = True
    doc = """Method defined in an Adapter Interface, will need implementation
    ----------------------------------------------------------------------------
    """
    method.__doc__ = doc + "\n" + method.__doc__
    method.__doc__ += """
    ----------------------------------------------------------------------------
    """
    return method

def modelmethod(method):
    """"Decorator, to be used to decorate a method a class that must
    take model as it's second argument. These methods must be implemented by
    an class that extends the containing class of these methods."""
    method.__ismodelmethod__ = True
    doc = """Method defined in validation test case's body to take 'model' as
    it's second argument. It must be defined by a class that extends the
    validation test case.
    ----------------------------------------------------------------------------
    """
    method.__doc__ = doc + '\n' + method.__doc__
    method.__doc__ += """
    ----------------------------------------------------------------------------
    """
    return method

def reportattribute(method):
    """Decorator, to be used to decorate a method of a class that must
    must be included in that class's ReportInterface.
    Normally such a class will be a test, and ReportInterface of that
    class will specify the type of report generated by that validation.
    Validation author is free to require any method in a report,
    but we request that they provide adequate documentation to help the users
    of their validation."""
    method.__isreportattribute__ = True
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


def is_adapter_method(method):
    """Specify the Protocol that an Adapter should implement a method. This
    method will be listed in an AdapterInterface."""
    return (isinstance(method, FunctionType) and
            getattr(method, '__isadaptermethod__', False))

def is_report_attribute(attr):
    """Specify the Protocol that a Report should have an attribute. This
    method will be listed a ReportInterface."""
    return getattr(attr, '__isreportattribute__')
    
def needs_adapter_interface(client_cls):
    """Specifies the protocol that a class specifies an interface.
    A class that has any method with attribute '__isadaptermethod__' set to
    'True' will be treated as specifying an interface.
    """
    return any([is_adapter_method(getattr(client_cls, method))
                for method in dir(client_cls)])
                                   
def get_interface(client_cls, name='Interface'):
    """Create an interface for a client class.
    Parameters
    ----------
    @client_cls :: type #the class that needs an interface."""
    if not needs_adapter_interface(client_cls):
        return None

    required = {m: getattr(client_cls, m) for m in dir(client_cls)
                if is_adapter_method(getattr(client_cls, m))}
    return type(name, (Interface, ), required)

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
    def __new__(mcs, name, bases, dct):
        cls = super(AIMeta, mcs).__new__(mcs, name, bases, dct)
        return cls

    def __init__(cls, name, bases, dct):
        ainame = "{}AdapterInterface".format(cls.__name__)
        adapter_interface = get_interface(cls, name=ainame)
        if not hasattr(cls, 'AdapterInterface') and adapter_interface:
            cls.AdapterInterface = adapter_interface

#        super(AIMeta, cls).__init__(name, bases, dct)


def adapter_documentation(cls):
    """Documentation of a class that will use an adapter."""
    return "AdapterInterface"

class AdapterInterfaceBase(Callable, metaclass=AIMeta):
    """A base class for classes that will declare an adapter interface.

    Initializer
    ----------------------------------------------------------------------------
    Pass a keyword argument 'model_adapter' to set the attribute _model_adapter.
    """

    _model_adapter = None

    def __init__(self, *args, **kwargs):
        self._model_adapter\
            = kwargs.get('model_adapter', kwargs.get('adapter', None))

    @property
    def model_adapter(self):
        """The adapter implementation to be used."""
        if self._model_adapter is None:
            raise Exception("An Adapter for {} was not set!!!"\
                            .format(self.__class__.__name__))
        return self._model_adapter

    @model_adapter.setter
    def model_adapter(self, value):
        """Reset the adapter."""
        self._model_adapter = value

    @property
    def adapter(self):
        """Another name for model_adapter.
        'model_adapter' is awkward. We went for this long form to keep open
        the possibility of having a 'data_adapter'. But looking towards a more
        generalized approach, you may also want to be able to validated two
        models against each other. The question is what will increase the
        overall usability of this framework.

        Thus on the side of simplicity, we argue for defining a validation
        along with the data --- that is data is part of a validation's
        definition. The more general notion may be defined as a 'Comparison'.
        We can have a hierarchy, starting with 'Analysis'.

        If we choose thus, then it makes sense that 'adapter' is always a
        'model_adapter'. We do not have to change the innards -- so protected
        variable name remains '_model_adapter'.
        """
        if self._model_adapter is None:
            raise Exception("An Adapter for {} was not set!!!"\
                            .format(self.__class__.__name__))
        return self._model_adapter

    @adapter.setter
    def adapter(self, value):
        """Reset the adapter, after testing that the new value is that of a
        valid implementation."""
        if self.AdapterInterface.is_implemented_by(value):
            self._model_adapter = value
        else:
            print(self.AdapterInterface.__implementation_guide__)
            raise ValueError("{} does not implement {} adapter's interface"\
                             .format(value, self.__class__.__name__))

    @classmethod
    def accepted_models(cls):
        """Models that this class with AdapterInterface will accept ---
        models for which at least one concrete implementation is available."""
        return set([
            get_adapted_entity(impl)
            for impl in implementation_registry(cls.AdapterInterface).values()
            if get_adapted_entity(impl) is not None
        ])

    def adapted(self, model):
        """Get an object that is an adapted model.
        Improve this documentation.
        """
        def __adapted_method(method):
            """..."""

            def __effective(this, *args, **kwargs):
                """..."""
                return getattr(self.adapter, method)(model, *args, **kwargs)

            return __effective

        name = "{}AdaptedTo{}".format(model.__class__.__name__,
                                      self.__class__.__name__)
        return type(name, (object, ), {
            m: __adapted_method(m)
            for m in self.AdapterInterface.__requiredmethods__
        })()
        

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
    return getattr(cls, '__requiredmethods__', [])

#and now the implementations
#def interface_implementation(an_interface):
def implementation(an_interface,
                   adapted_entity=None,
                   reported_entity=None):
    """A class decorator to declare that a class implements an interface, which
    may either adapt a Model or Data-object to a Validation, or may implement a
    reporter class.
    ---------------------------------------------------------------------------

    Parameters
    ---------------------------------------------------------------------------
    an_interface :: Interface# mostly generated with an appropriate decorator
    adapted_entity :: MeasurableSystem# model / data that was adapted
    reported_entity :: Analysis #in most cases that I can think of!
    ---------------------------------------------------------------------------

    Protocol
    ---------------------------------------------------------------------------
    A class 'cls' is an interface implementation
    if cls.__isinterfaceimplementation__ == True
    ---------------------------------------------------------------------------
    """
    if not issubclass(an_interface, Interface):
        raise Exception("{} is not an Interface".format(an_interface))

    def effective(cls):
        """Effective class"""
        if not hasattr(cls, 'author'):
            #ISSUE A WARNING HERE with the following message
            print("Interface {} implementation {} should attribute its author"\
                  .format(an_interface.__name__, cls.__name__))
            cls.author = Author.anonymous
            print("Here we will assume that the author is Anonymous\n",
                  cls.author)
        an_interface.register_implementation(cls)
        cls.__isinterfaceimplementation__ = True
        cls.__implemented_interface__ = an_interface
        if adapted_entity is not None and reported_entity is not None:
            raise ValueError("""
            Only one of 'adapted_entity', 'reported_entity'
            may be passed as an argument!!!
            """)
        if adapted_entity is not None:
            cls.__adapted_entity__ = adapted_entity
        if reported_entity is not None:
            cls.__reported_entity__ = reported_entity
        return cls

    return effective

implements = implementation #just an alias

def get_implementations(an_interface):
    """all the implementations"""
    if not isinstance(an_interface, Interface):
        raise Exception("{} is not an Interface!!!"\
                        .format(an_interface.__name__))
    return an_interface.__implementation_registry__
        
def get_adapted_entity(impl):
    """Get models implemented by an implementation.
    We assume that one implementation will adapt only one model type."""
    return getattr(impl, '__adapted_entity__', None)

                
def is_model_method(base_cls, method):
    """Is 'method' a model method of class 'base_cls'?"""
    return getattr(getattr(base_cls, method, None), '__ismodelmethod__', False)

def extends(base_cls):
    """A class decorator to mark a class that extends a base class."""
    required_model_methods = [method for method in dir(base_cls)
                              if is_model_method(base_cls, method)]
    def effective(sub_cls):
        """Effective class. Move to base_cls methods of sub_class,
        that are not in base_cls already"""
        def combined_init(self, *args, **kwargs):
            """Combined initialization."""
            #sub_cls.__init__(self, *args, **kwargs)
            self.__init__(*args, **kwargs)

        #attrs = {'__init__': combined_init}
        attrs = {}
        for model_method in required_model_methods:
            if hasattr(sub_cls, model_method):
                attrs[model_method] = getattr(sub_cls, model_method)
            else:
                print("WARNING: {} does not provide all model methods of {}"\
                      .format(sub_cls, base_cls))

        return type(sub_cls.__name__, (base_cls,), attrs)

    return effective

def modelextension(validation_cls):
    """A class decorator to convert a 'ValidationTestCase' to a full validation
    by implementing 'modelmethods' (look at decorator method 'modelmethod'). For
    now it acts like an alias for 'extends'.
    """
    return extends(validation_cls)
