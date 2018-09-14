"""Parameters relevant for neuroscience measurements ---
these can be used as base classes by model adapters, and required and coded
against by validation authors. The author of a model adapter then has to just
look up the documentation to write an appropriate base class."""

from abc import ABC, abstractmethod
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import ClassAttribute, Field

class Layer(FiniteValuedParameter):
    """An abstract base class to represent a generic layer in any brain region.
    Model Adaptors must implement the interface presented here to use
    validations from our library. We will specialize a Layer's attributes
    in several stages of sub-classing."""
    label = "Layer"

class CorticalLayer(Layer):
    """A layer in the cortex."""
    value_type = int

    def __init__(self, *args, **kwargs):
        """Default cortical layer will have int values 1, 2, 3, 4, 5, and 6.
        The user may override this initializer."""
        kwargs.update({
            "value_order": {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5},
            "repr_dict": {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"} 
        })
        super(CorticalLayer, self).__init__(*args, **kwargs)


class HippocampalLayer(Layer):
    """Layer in the hippocampus."""
    value_type = str
    def __init__(self, *args, **kwargs):
        """Default hippocampal layer will have int values 'SLM', 'SR', 'SP',
        and 'SO'. The user may override this initializer."""
        kwargs.update({
            "value_order": {"SLM": 0, "SR": 1, "SP": 2, "SO": 3},
            "repr_dict":  {"SLM": "SLM", "SR": "SR", "SP": "SP", "SO": "SO"}
        })
        super(HippocampalLayer, self).__init__(*args, **kwargs)
