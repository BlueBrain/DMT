"""A measurement parameter may need to be printed
differently than it's actual value.
For example for layer r4 we want to see either
(deprecated by a millennium) Roman letters IV, or L-IV.
To allow this divergence between it's actual value and it's representation,
we define class Parameter."""

from abc import ABC, abstractmethod
import collections
import numpy as np
import pandas as pd
from dmt.vtk.utils.descriptor import ClassAttribute, Field
from dmt.vtk.utils.collections import Record, take
from dmt.vtk.utils.pandas import flatten, level_values

class Parameter(ABC):
    """Base class to define a measurement parameter.
    While a Parameter can be defined theoretically, we will be
    interested Parameters in the context of a particular model.
    """
    label = Field(
        __name__ = "label",
        __type__ = str,
        __doc__  = """A short name for this Parameter -- no spaces."""
    )
    value_type = Field(
        __name__ = "value_type",
        __type__ = type,
        __doc__  = """Type of the values assumed by this Parameter."""
    )
    @abstractmethod
    def values(self, *args, **kwargs):
        """Values assumed by the model.

        Return
        -----------------------------------------------------------------------
        iterable (generator for infinite parameters)
        """
        pass

    def __init__(self, *args, **kwargs):
        pass

    def is_valid(self, value):
        """Is value 'v' an accepted value?
        We provide a default value, the subclass may override."""
        return isinstance(value, self.value_type)

    def order(self, value):
        """
        Where is value in relation to other values of this Parameter?
        We provide a default implementation, assuming that value itself
        is ordered. The user who knows better may adapt to her needs.
        Return
        ------------------------------------------------------------------------
        <: OrderedType
        """
        return value

    def repr(self, value):
        """Representation of value 'value' of this Parameter.

        Parameters
        ------------------------------------------------------------------------
        value :: ValueType #a value of this parameter.

        Implementation Notes
        ------------------------------------------------------------------------
        We provide a default implementation. You may generalize it.
        """
        assert(self.is_valid(value))
        return "{}".format(value)

