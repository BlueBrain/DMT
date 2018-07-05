"""An abstract class that will create an interface for a model."""
from abc import ABC, abstractmethod

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




def interface(cls):
   """a class decorator that issues Interface"""
   
   cls.registry = {}
   msg = "Interface " + cls.__name__ + " requires you to implement\n"
                               
   n = 1
   for m in cls.__abstractmethods__:
      mm = getattr(cls, m)
      msg  += "\t(" + str(n) + ") " + m + ":\n\t\t"
      msg += mm.__doc__ + "\n"
      n += 1

   cls.guide =  msg

   return cls

def get_implementations(an_interface):
   return an_interface.registry

def implements(an_interface):
   """a class decorator to declare that a class implements an interface.
   Improvements
   ------------
   Do we need  consider that interface implementations
   may implement the required methods as abstract?"""

   def class_implements(cls):
      for m in an_interface.__abstractmethods__:
         if not hasattr(cls, m): 
            print(an_interface.guide)
            raise Exception("Unimplemented required method '" + m +
                            "' a by interface " + an_interface.__name__)

      an_interface.registry[cls.__name__] = cls
      return cls

   return class_implements
