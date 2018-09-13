"""Utility class to work with brain regions.
This is a good playground to understand descriptors and type validations."""

from abc import ABC, abstractmethod

def label(brain_region_type):
    return brain_region_type.__label__

class BrainRegion(ABC):
    """Base class regions of the brain.

    Attributes
    ----------------------------------------------------------------------------
    __subtypes__ :: Dict
    __values__ :: List, or a Generator ()

    __label__ :: String #deriving class should modify, eg Cortical Layer.
    """

    label = "region"

    subtypes = {} #may not be necessary

    values = [] #may not be necessary

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
    def __str__(self):
        pass

    def __repr__(self):
        """represent this BrainRegion"""
        return "{}({})".format(self.__class__.__name__, self.__str__)

    
class Layer(BrainRegion):
    """Layer is a type of brain region.
    Still abstract class."""
    label = "Layer"
    pass


class CorticalLayer(Layer):

    @property
    def __str__(self):
        return {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}[self._value]
        

CorticalLayer.values\
    = [CorticalLayer(l) for l in range(1, 7)]

class HippocampalLayer(Layer):

    @property
    def __str__(self):
        return self._value

HippocampalLayer.values\
    = [HippocampalLayer(l) for l in ['SLM', 'SR', 'SP', 'SO']]
                               
