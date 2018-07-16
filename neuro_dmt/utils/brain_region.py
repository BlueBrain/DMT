"""Utility class to work with brain regions.
This is a good playground to understand descriptors and type validations."""

from abc import ABC, abstractmethod
class BrainRegionType(ABC):
    """Base class regions of the brain.
    ABC with an abstractmethod, because we do not want """

    __subtypes__ = {}

    __values__ = []

    """Layer in the cortex."""
    def __init__(self, value):
        """For the cortex, the layer labels will be L1, L2, ..."""
        self._value = value

    @classmethod
    def add_subtype(cls, subtype):
        """Add a subtype."""
        cls.__subtypes__[subtype.__name__] = subtype

    @classmethod
    def add_values(cls, value):
        """Check that value is of type cls and append to values."""
        assert(isinstance(value, cls))
        cls.values.append(value)
        
    @property
    @abstractmethod
    def label(self):
        """Label that can be used."""
        pass

    def __repr__(self):
        """represent this BrainRegionType"""
        return "{}({})".format(self.__class__.__name__, self.label)

    
class Layer(BrainRegionType):
    """Layer is a type of brain region.
    Still abstract class."""
    pass


class CorticalLayer(Layer):

    @property
    def label(self):
        return "L{}".format(self._value)
        

CorticalLayer.__values__ = [CorticalLayer(l)
                            for l in ['1', '2', '3a', '3b', '3',
                                      '4', '5a', '5b', '5', '6a', '6b', 6]]

class HippocampalLayer(Layer):

    @property
    def label(self):
        return self._value

HippocampalLayer.__values__ = [HippocampalLayer(l)
                               for l in ['SLM', 'SR', 'SP', 'SO']]
