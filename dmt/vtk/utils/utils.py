"""General utilities."""

from abc import ABCMeta, abstractmethod
import collections

class ABCwithRegistryMeta(collections.Mapping, ABCMeta):
    """An ABC that keeps a registry of its implementaions.
    We can use this meta-class to define an ABC for models,
    data-objects, and validations providing them with a
    registry for implementations."""

    def __new__(meta, name, bases, dct):
        #return super(ABCwithRegistryMeta, meta).__new__(meta, name, bases, dct)
        return ABCMeta.__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, namespace):
        super(ABCwithRegistryMeta, cls).__init__(name, bases, namespace)

        if not hasattr(cls, '__implementation_registry__'):
            cls.__implementation_registry__ = {}

        #we register only concrete implementations of ABC cls
        if not isabstract(cls):
            cls.__implementation_registry__[cls.__name__] = cls

    def __iter__(cls):
        """iterate concrete implementations with items(cls)"""
        return iter(cls.__implementation_registry__)

    def __len__(cls):
        return len(cls.__implementation_registry__)

    def __getitem__(cls, key):
        return cls.__implementation_registry__[key]

    def __str__(cls):
        """Get a description"""
        return (
            cls.__name__ + ": " + (", ").join(
                cls.keys() if isabstract(cls) else
                [cls.__name__] + [s.__name__ for s in cls.__subclasses__()]
            ))

    def __hash__(cls):
        return hash(str(cls))

    def __repr__(cls):
        """Get a representation"""
        return str(cls)
                                                    

        


#methods

def isabstract(cls):
    """is the class cls abstract?"""
    return (hasattr(cls, '__abstractmethods__') and
            isinstance(cls.__abstractmethods__, collections.Iterable) and
            len(cls.__abstractmethods__) > 0)


def get_file_name_base(file_name=None):
    """Get the base from a file name, stripping away it's suffix."""
    return ("report" if file_name is None else
            '_'.join(file_name.split('.')[0:-1]).strip().replace(' ', '_'))
