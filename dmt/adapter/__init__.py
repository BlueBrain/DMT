"""We cannot always assume that the author of a validation test case to use the
same method names as those provided by the API exposed by the model that the
author wants to validate. This assumption will hold where the author of the
validation has also authored the model, or is well versed with the model API.
However, validations written with a particular model in mind cannot be
generalized to other models.

However, if the author codes her Validation using an interface her Validation
can be used by another user. Our DMT framework will provide advice to a user
intends to use a Validation"""

class InterfaceMeta(type):
    """A metaclass to be used to create Interfaces!
    This metaclass will strip away any implementation of a method.
    This will define a strict interface, that cannot be implemented,
    can is not allowed to have any methods with implementations in
    its body."""

    def __init__(meta,  name, bases, attrs):
        """..."""
        def raise_not_implemented(function):
            """..."""
            def function_eff(*args, **kwargs):
                raise NotImplementedError

            function_eff.__doc__ = function.__doc__
            return function_eff

        for k in attrs.keys():
            attrs[k] = raise_not_implemented(attrs[k])

        super(InterfaceMeta, meta).__init__(name, bases, attrs)
    

class Interface(metaclass=InterfaceMeta):
    """An Interface cannot be implemented!"""

    def __init__(self, *args, **kwargs):
        raise Exception("{} is an Interface\n".format(self.__class__.__name__) + 
                         "An Interface cannot be initialized.\n" +
                        "It must be implemented!!!\n")

def interface(client_cls, prefix=""):
    """Create an adapter interface for a client class.
    Parameters
    ----------
    @client_cls :: the client class that needs an interface for a (model)
    adapter as specified by methods marked __requiredmethod__.

    Implementation Notes
    --------------------
    We establish a Protocol: any methods marked '__requiredmethod__' will be
    considered as requirements of an adapter that needs to be implemented
    to use the client class."""

    required = {
        m: getattr(client_cls, m) for m in dir(client_cls)
        if getattr(getattr(client_cls, m), '__isrequiredmethod__', False)
    }
    cname = client_cls.__name__
    suffix = prefix + ("" if (cname.endswith("Interface")
                              or cname.endswith("interface"))
                       else "Interface")

    adapter_spec = type(client_cls.__name__ + suffix, (Interface,), required)

    adapter_spec.__requiredmethods__ = required.keys()

    adapter_spec.__implementation_registry__ = {}

    msg = "AdapterInterface for {} requires you to implement\n"\
          .format(client_cls.__name__)
    n = 1
    for m, mm in required.items():
        mm = getattr(client_cls, m)
        msg += "\t({}) {}: ".format(str(n), m)
        msg += (mm.__doc__ if mm.__doc__ else "") + "\n"
        n += 1

    client_cls.guide = msg
    adapter_spec.guide = msg

    return adapter_spec

def implementations(an_interface):
   return an_interface.__implementation_registry__

def provided(required_method):
    """To decorate methods that should be provided by an adapter."""
    required_method.__isrequiredmethod__ = True
    return required_method

requires = provided

def implements(an_interface):
   """a class decorator to declare that a class implements an interface.
   Improvements
   ------------
   Do we need consider that interface implementations
   may implement the required methods as abstract?"""

   def class_implements(cls):
      for m in an_interface.__requiredmethods__:
         if not hasattr(cls, m):
            print(an_interface.guide)
            raise Exception("Unimplemented required method '" + m +
                            "' a by interface " + an_interface.__name__)

      an_interface.__implementation_registry__[cls.__name__] = cls
      return cls

   return class_implements


def adapt(client_cls):
    """a method intended to decorate classes that will need an
    AdapterInterface, that can be used instead of metclass=AIMeta"""
    client_cls.AdapterInterface = interface(client_cls, prefix='Adapter')
    return client_cls


from abc import ABCMeta

class AIMeta(ABCMeta):
    """A metaclass that will add an AdapterInterface."""

    def __new__(meta, name, bases, dct):
        return super(AIMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        cls.AdapterInterface = interface(cls)
        super(AIMeta, cls).__init__(name, bases, dct)

