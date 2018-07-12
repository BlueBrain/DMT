"""We cannot always assume that the author of a validation test case to use the
same method names as those provided by the API exposed by the model that the
author wants to validate. This assumption will hold where the author of the
validation has also authored the model, or is well versed with the model API.
However, validations written with a particular model in mind cannot be
generalized to other models.

However, if the author codes her Validation using an interface her Validation
can be used by another user. Our DMT framework will provide advice to a user
intends to use a Validation"""



def interface(client_cls):
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
    adapter_spec = type(client_cls.__name__ + 'AdapterInterface',
                        (object,), required)

    adapter_spec.__requiredmethods__ = required.keys()

    adapter_spec.__implementation_registry__ = {}

    msg = "AdapterInterface for {} requires you to implement\n"\
          .format(client_cls.__name__)
    n = 1
    for m, mm in required.items():
        mm = getattr(client_cls, m)
        msg += "\t({}) {}: ".format(str(n), m)
        msg += mm.__doc__ + "\n"
        n += 1

    client_cls.guide = msg

    return adapter_spec


def interface0(adapter_spec):
   """Using the specification in adapter_spec, """

   adapter_spec.__implementation_registry__ = {}
   msg = "Interface " + adapter_spec.__name__ + " requires you to implement\n"

   n = 1
   for m in adapter_spec.__requiredmethods__:
      mm = getattr(adapter_spec, m)
      msg  += "\t(" + str(n) + ") " + m + ": "
      msg += mm.__doc__ + "\n"
      n += 1

   adapter_spec.guide =  msg

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


def get_adapter_interface(cls):
    """define an adapter for a class."""
    required = {m: getattr(cls, m) for m in dir(cls)
                if getattr(getattr(cls, m), '__isrequiredmethod__', False)}
    adapter_spec = type(cls.__name__ + 'AdapterInterface', (object,), required)
    adapter_spec.__requiredmethods__ = required.keys()
    return interface0(adapter_spec, cls)

def adapt(cls):
    cls.AdapterInterface = get_adapter_interface(cls)
    return cls
