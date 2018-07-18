"""We cannot assume that the authors of validation test cases and models will
use identical method names for measuring the model's phenomena. So we have to
code a validation using the interface of a model adapter. This interface will
effectively list all the methods that a concrete implementation of this
model adapter will have to implement.

Notes
-----
(20180712) This implementation has been abandoned in favor of decorators."""

from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    """A ModelAdapter adapts a model to an interface."""

    @abstractmethod
    def adapts(self, model):
        """Check if this ModelAdapter has implemented all the required
        methods."""
        pass

    @abstractmethod
    def get_measurement(self, measurable_system):
        """get the measurement.

        Parameters
        ----------
        @measurable_system :: MeasurableSystem

        Return
        -------
        Measurement

        """
        pass

class Interface(ABC):
   """A metaclass that will create an interface like object.
   Notes
   ---------
   1. A Utility object can specify it's requirements from an argument as an
   Interface subclass. The user can adapt her class directly to the Interface's
   specification, or she can write an Adapter that wraps the model she intends
   the Utility to work with. An 'adapted' object will thus be sent as an
   argument to the Utility, which will call the methods declared in the
   Interface on the adapted model object. The adapted model will simply pass
   these method calls onto the actual model.

   2. If the object passed to a Utility's __call__ method does not
   satisfy its Interface, the Utility should throw a descriptive exception
   that the user can use to re/implement an Adapter that provides the required
   ModelInterface for the model of interest.

   3. This must be a metaclass because we want all the methods declared by the
   a 'subclass' to be abstract. The user does not have to declare them as
   abstract, as they do when writing an ABC. They can just leave the body of
   the method unfilled. The whole purpose will be:
     3a. specify method names
     3b. suggest method calling signatures and return type through suggestive
     argument names and documentation
     3c. describe what the method is about through the doc-string.
   So the __new__ method the metaclass must define should take the attribute
   names and make them abstract!

   Guidelines on implementing a ModelInterface
   -------------------------------------------
   1. as a first attempt, define your interface methods with an @abstractmethod
   decorator, provide documentation on what the method is supposed to do and its
   argument types and return type and 'pass' as the method's body.
   """

   @classmethod
   def implementation_guide(cls):
      message = "Interface " + cls.__name__ + " requires you to implement\n" 
      n = 1

      for m in cls.__abstractmethods__:
         mm = getattr(cls, m)
         msg  += "\t(" + str(n) + ") " + m + ":\n\t\t"
         msg += mm.__doc__
         n += 1

      return message + "\n"


