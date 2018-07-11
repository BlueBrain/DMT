"""General utilities."""

from abc import ABCMeta, abstractmethod
import collections
#import inspect
import dmt.utils.utils as utils

class ABCwithRegistryMeta(collections.Mapping, ABCMeta):
    """An ABC that keeps a registry of its implementaions.
    We can use this meta-class to define an ABC for models,
    data-objects, and validations providing them with a
    registry for implementations."""

    def __new__(meta, name, bases, dct):
        return super(ABCwithRegistryMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, namespace):
        super(ABCwithRegistryMeta, cls).__init__(name, bases, namespace)

        if not hasattr(cls, '_implementation_registry'):
            cls._implementation_registry = {}

        #we register only concrete implementations of ABC cls
        if not utils.isabstract(cls):
            cls._implementation_registry[cls.__name__] = cls

    def __iter__(cls):
        """iterate concrete implementations with items(cls)"""
        return iter(cls._implementation_registry)

    def __len__(cls):
        return len(cls._implementation_registry)

    def __getitem__(cls, key):
        return cls._implementation_registry[key]

    #def __str__(cls):
    #    """Get a description"""
    #    if cls.__name__ in cls._implementation_registry:
    #        return cls.__name__
    #    return cls.__name__ + ": " + ", ".join(cls._implementation_registry.keys())

    def __str__(cls):
        """Get a description"""
        return (
            cls.__name__ + ": " + (", ").join(
                cls.keys() if utils.isabstract(cls) else
                [cls.__name__] + [s.__name__ for s in cls.__subclasses__()]
            ))

    def __repr__(cls):
        """Get a representation"""
        return str(cls)
                                                    

        


#methods

def isabstract(cls):
    """is the class cls abstract?"""
    return (hasattr(cls, '__abstractmethods__') and
            isinstance(cls.__abstractmethods__, collections.Iterable) and
            len(cls.__abstractmethods__) > 0)
