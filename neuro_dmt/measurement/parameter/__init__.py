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
    in several stages of sub-classing.

    Notes
    ----------------------------------------------------------------------------
    If we want the two ends of a validation to work independently, then
    Parameter should be a mechanism of communication. Parameter can be used to
    set the protocol.
    """
    label = "layer"


class CorticalLayer(Layer):
    """A layer in the cortex."""
    value_type = int

    def __init__(self, *args, **kwargs):
        """Default cortical layer will have int values 1, 2, 3, 4, 5, and 6.
        The user may override this initializer."""
        super(CorticalLayer, self).__init__(
            value_order={1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5},
            value_repr={1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"},
            *args, **kwargs
        )

class CorticalLayer23Fused(Layer):
    """Represents cortical layers, when layers 2 and 3 are fused into one."""
    value_type = int

    def __init__(self, *args, **kwargs):
        """..."""
        super(CorticalLayer23Fused, self).__init__(
            value_order={1: 0 , 2: 1, 3: 1, 4: 2, 5: 3, 6: 4},
            value_repr={1: "I", 2: "II/III", 3: "II/III", 4:"IV", 5: "V", 6: "VI"},
            *args, **kwargs
        )

class CorticalLayer5abSplit(Layer):
    """Represents cortical layers when layer 5 is split into 5a, and 5b."""
    value_type = str

    def __init__(self, *args, **kwargs):
        """..."""
        super(CorticalLayer5abSplit, self).__init__(
            value_order={"1": 0, "2": 1, "3": 2, "4": 3,
                         "5a": 4, "5b": 5, "6": 6},
            value_repr={"1": "I", "2": "II", "3": "III",
                        "4": "IV", "5a": "Va", "5b": "Vb", "6": "VI"},
            *args, **kwargs
        )

class HippocampalLayer(Layer):
    """Layer in the hippocampus."""
    value_type = str

    def __init__(self, *args, **kwargs):
        """Default hippocampal layer will have int values 'SLM', 'SR', 'SP',
        and 'SO'. The user may override this initializer."""
        super(HippocampalLayer, self).__init__(
            value_order={"SLM": 0, "SR": 1, "SP": 2, "SO": 3},
            value_repr={"SLM": "SLM", "SR": "SR", "SP": "SP", "SO": "SO"},
            *args, **kwargs
        )
