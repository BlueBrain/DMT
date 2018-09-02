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
from dmt.vtk.utils.descriptor import ClassAttribute
from dmt.vtk.utils.collections import Record

class Parameter(ABC):
    """Base class to define a measurement parameter.
    While a Parameter can be defined theoretically, we will be
    interested Parameters in the context of a particular model.
    """
    label = ClassAttribute(
        __name__ = "label",
        __type__ = str,
        __doc__  = """A short name for this Parameter -- no spaces."""
    )
    value_type = ClassAttribute(
        __name__ = "value_type",
        __type__ = type,
        __doc__  = """Type of the values assumed by this Parameter."""
    )
    @property
    @abstractmethod
    def values(self):
        """Values assumed by the model.

        Return
        -----------------------------------------------------------------------
        Iterable.
        """
        pass

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def is_valid(self, value):
        """Is value 'v' an accepted value?"""
        pass

    @property
    @abstractmethod
    def order(self, value):
        """
        Where is value in relation to other values of this Parameter?
        Represented as an int.
        Use ascending order, and positive values --- thus a value of 1 is
        the smallest.

        Return
        ------------------------------------------------------------------------
        int #positive integer > 0 that represents the order of value. 
        """
        pass

    @abstractmethod
    def repr(self, value):
        """Representation of value 'value' of this Parameter.

        Parameters
        ------------------------------------------------------------------------
        value :: ValueType #a value of this parameter.

        Implementation Notes
        ------------------------------------------------------------------------
        Implement this method as a class method.
        """
        pass

    def random_value(self, n=None):
        """Get n random values.
        Values will be replaced after each choice.

        Return
        ------------------------------------------------------------------------
        value_type #if n is None
        [value_type] #if n is not None
        """
        return np.random.choice(self.values, n)


class GroupParameter(Parameter):
    """A parameter that groups another. For example in a brain,
    Layer is a parameter that groups positions in a brain region.
    """
    grouped_variable = ClassAttribute(
        __name__ = "grouped_type",
        __type__ = Record,
        __is_valid_value__ = (
            lambda r: hasattr(r, '__type__') and hasattr(r, 'name')
        ),
        __doc__  = """Type grouped by this GroupParameter."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        super(GroupParameter, self).__init__(*args, **kwargs)

    @abstractmethod
    def __call__(self, model, n=None):
        """Collect a sample of the grouped type in the context of a model.

        Return
        ------------------------------------------------------------------------
        grouped_variable.__type__
        """
        pass


def get_values(parameters):
    """Generate values for parameters in the list 'parameters'.

    Parameters
    ----------------------------------------------------------------------------
    group_parameters :: List[<:GroupParameter] #list of GroupParameter subclasses

    Return
    ----------------------------------------------------------------------------
    pandas.DataFrame
    """
    def __get_value_tuples(params):
        """..."""
        p0 = params[0]
        if len(params) == 1:
            return [ [(p0.label, v)] for v in p0.values]
        
        return [[(p0.label, v)] + pvs
                for v in p0.values for pvs in __get_value_tuples(params[1:])]

    return pd.DataFrame([dict(t) for t in __get_value_tuples(parameters)])

def get_grouped_values(group_params, *args, **kwargs):
    """Generate values for parameters in the list 'parameters'.

    Parameters
    ----------------------------------------------------------------------------
    group_parameters :: List[<:GroupParameter] #list of GroupParameter subclasses

    Return
    ----------------------------------------------------------------------------
    dict
    """
    def __get_tuples(params):
        """..."""
        if len(params) == 0:
            return ()
        p0 = params[0]
        print("get tuples for {} parameters with 0th: {}".format(len(params), p[0]))
        vs0 = ([(p0.grouped_variable.name, grouped_value), (p0.label, value)]
               for (value, grouped_value) in p0(*args, **kwargs))
        return (vs0 if len(params) == 1 
                else [v + pvs for v in vs0 for pvs in __get_tuples(params[1:])])

    return pd.DataFrame([dict(t) for t in __get_tuples(group_params)])

