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
from dmt.vtk.utils.collections import Record, take

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


    def filled(self, dataframe, ascending=True):
        """Filled and sorted Dataframe by index,
        which is of the type of this Parameter."""
        missing = list(self.values - set(dataframe.index))
        missing_df = pd.DataFrame({'mean': len(missing) * [0.],
                                   'std': len(missing) * [0.]})
        full_df = pd.concat(dataframe, missing_df)
        index = pd.Index([self.repr(i) for i in full_df.index],
                         dtype="object", name=self.label)
        full_df.index = index
        full_df["order"] = [self.order(v) for v in dataframe.index]
        return full_df.sort_values(by="order")[["mean", "std"]]


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
        __doc__  = """Metadata for the variable grouped by this GroupParameter."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        super(GroupParameter, self).__init__(*args, **kwargs)

    @abstractmethod
    def random_grouped_values(self, value):
        """All the values of the grouped variable covered by value 'value' of
        this GroupParameter. 

        Parameters
        ------------------------------------------------------------------------
        value :: self.value_type #

        Return
        ------------------------------------------------------------------------
        Generator[Tuple(self.value_type, self.grouped_variable.type)]
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
    n = kwargs.get("sample_size", 20)
    for p in group_params:
        for v in p.values:
            xs = [x.bbox
                  for x in take(n, p.random_grouped_values(v, *args, **kwargs))]
            print("value grouped under {} value {} found {}".format(v, p, len(xs)))

    def __get_tuples(index):
        """..."""
        if index == len(group_params):
            return ()
        p0 = group_params[index]
        vs0 = [[(p0.grouped_variable.name, gv), (p0.label, v)]
               for v in p0.values
               for gv in take(n, p0.random_grouped_values(v, *args, **kwargs))]
        if index + 1 == len(group_params):
            return vs0
        else:
            vsrest = __get_tuples(index + 1)
            return [v0 + v1 for v0 in vs0 for v1 in vsrest]

    return pd.DataFrame([dict(t) for t in __get_tuples(0)])

