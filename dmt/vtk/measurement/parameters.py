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
    _possible_values = ClassAttribute(
        __name__ = "possible_values",
        __type__ = collections.Iterable,
        __doc__  = """All possible values assumed by this Parameter.
        This may be a list, or a generator, or your custom Iterable."""
    )
    def __init__(self, v, *args, **kwargs):
        """Initialize with value v."""
        if not isinstance(v, self.value_type):
            raise TypeError("{} is not the expected type {}"\
                            .format(v, self.value_type))
        self._value = v

    @property
    def value(self):
        return self._value

    @property
    @abstractmethod
    def _has_valid_value(self):
        """Is 'value' an accepted value?"""
        pass

    @property
    @abstractmethod
    def order(self):
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
    def __repr__(self):
        """Representation of a value of this Parameter.

        Parameters
        ------------------------------------------------------------------------
        value :: ValueType #a value of this parameter.

        Implementation Notes
        ------------------------------------------------------------------------
        Implement this method as a class method.
        """
        pass

    @property
    def is_valid(self):
        """Is value 'v' an accepted value?"""
        return self._has_valid_value

    @classmethod
    def random_value(cls, n=None):
        """Get n random values.
        Values will be replaced after each choice.

        Return
        ------------------------------------------------------------------------
        value_type #if n is None
        [value_type] #if n is not None
        """
        return cls(np.random.choice(cls._possible_values, n))


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
        Tuple(value_type, grouped_type)
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

def get_grouped_values(group_params, *model_args):
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
        p0 = params[0]
        vs0 = ([(p0.grouped_variable.name, grouped_value), (p0.label, v)]
               for v in p0._possible_values
               for grouped_value in p0(v)(*model_args))
               
        return (vs0 if len(params) == 1 
                else [v + pvs for v in vs0 for pvs in __get_tuples(params[1:])])

    return pd.DataFrame([dict(t) for t in __get_tuples(group_params)])

                         

