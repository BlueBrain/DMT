"""aii is Adapter, Interface, and (their) Implementations.
A validation should employ a language of the problem domain, and not be
specialized for a particular problem domain. So the validation code in a
ValidationTestCase must interface with a model through an adapter. The author
of a ValidationTestCase must mark the methods required from the Adapter with
decorators '@interfacemethod'. To use a ValidaionTestCase for a particular
model, the user must provide an adapter implementation."""

from types import FunctionType
from abc import ABC, ABCMeta, abstractmethod
from dmt.vtk.utils.descriptor import ClassAttributeMeta
from dmt.aii.interface import \
    get_interface, interfacemethod, interfaceattribute, get_implementations
from dmt.aii.adapter import get_types_adapted
from dmt.vtk.author import Author

class Callable(ABC):
    """A simple extension of ABC,
    with an init method that takes *args and **kwargs,
    but only to ignore them.
    This is required because abc.ABC.__init__ does not take any parameters"""
    def __init__(self, *args, **kwargs):
        """init"""
        super(Callable, self).__init__() #or don't do anything
    
def requiredmethod(method):
    """Decorator, to be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method.__isrequiredmethod__ = True
    return method

def adaptermethod(method):
    """Decorator, to be used to decorate a method of a class that must
    be included in that class's AdapterInterface."""
    method = interfaceattribute(method)
    method = interfacemethod(method)
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

def is_required_method(method):
    """Specify the protocol that a method is required by an interface."""
    return (isinstance(method, FunctionType) and
            getattr(method, '__isrequiredmethod__', False))


def is_adapter_method(method):
    """Specify the Protocol that an Adapter should implement a method. This
    method will be listed in an AdapterInterface."""
    return (isinstance(method, FunctionType) and
            getattr(method, '__isinterfacemethod__', False))


class AIMeta(ABCMeta, ClassAttributeMeta):
    """A metaclass that will add an AdapterInterface."""
    def __new__(mcs, name, bases, dct):
        """Give an AdapterInterface to class 'cls' only if it does not
        have one already.

        Proposed Tests and Improvements
        ------------------------------------------------------------------------
        The user might be clumsy and add some adaptermethods in a subclass. We
        need to test this behavior.
        In the current implementation, if a class already has an 
        AdapterInterface we do not do anything. As an improvement, we can
        add methods to the existing AdapterInterface --- or set it as a
        base-class of a newly defined AdapterInterface.
        """
        #print("construct {} with AIMeta and methods {}".format(name, dct.keys()))
        if 'AdapterInterface' not in dct:
            ainame = "{}AdapterInterface".format(name)
            adapter_interface = get_interface(dct, name=ainame)
            if adapter_interface is not None:
                dct['AdapterInterface'] = adapter_interface
            else:
                print("""WARNING!!! 
                AIMeta could not find or create an AdapterInterface
                for {}
                """.format(name))
        cls = super(AIMeta, mcs).__new__(mcs, name, bases, dct)
        return cls

    def __init__(cls, name, bases, dct):
        """No specific metalcass initialization for now.
        """
        super(AIMeta, cls).__init__(name, bases, dct)


def adapter_documentation(cls):
    """Documentation of a class that will use an adapter."""
    return "AdapterInterface"

class AIBase(Callable, metaclass=AIMeta):
    """A base class for classes that will declare an adapter interface.

    Initializer
    ----------------------------------------------------------------------------
    Pass a keyword argument 'model_adapter' to set the attribute _model_adapter.
    """

    _model_adapter = None

    def __init__(self, *args, **kwargs):
        #self._model_adapter\
        an_adapter = kwargs.get('model_adapter', kwargs.get('adapter', None))
        if an_adapter:
            self.adapter = an_adapter #validate and assign
        else:
            self._model_adapter = None

        super(AIBase, self).__init__(*args, **kwargs)

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
        adapted_entities = {}
        for impl in get_implementations(cls.AdaptedInterface).values():
            adapted_entities.update(get_types_adapted(impl))
        return adapted_entities
        #adapted_entities \
        #    = {k: v for k, v in get_adapted_types(impl).items()
        #       for impl in get_implementations(cls.AdapterInterface).values()]
        #return list(set([ae for ae in adapted_entities if ae is not None]))

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
            for m in self.AdapterInterface.__interfacemethods__
        })()
        
                
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
