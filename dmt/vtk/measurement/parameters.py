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
    @abstractmethod
    def values(self, *args, *kwargs):
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

class Grouper:
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

    def __call__(self, size=20):
        """Return a Pandas Series of size 'size'."""



class FiniteValuedParameter(Parameter):
    """If the number of all possible values of a parameter is finite,
    we can require certain finite data representations of its attributes,
    and adapt Parameter abstractmethods."""
    value_type = ClassAttribute(
        __name__ = "value_type",
        __type__ = type,
        __doc__  = """Type of the values assumed by this Parameter."""
    )
    value_order = Field(
        __name__ = "__value_order__",
        __type__ = dict, 
        __is_valid_value__ = lambda self, value_order_dict: all(
            (isinstance(value, self.value_type) and
             isinstance(order, int) and order >= 0)
            for value, order in value_order_dict.items()
        ),
        __doc__="""A dict mapping values to their order.""" 
    )
    repr_dict = Field(
        __name__ = "repr_dict",
        __type__ = dict,
        __is_valid_value__ = lambda self, vrdict: all(
            isinstance(value, self.value_type) and isinstance(rep, str)
            for value, rep in vrdict.items()
        ),
        __doc__="""A dict mapping values to their string representation. You
        may not pass this value to this base class' initializer. There will be
        a default implementation."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        self.value_order = kwargs.get("value_order", None)
        self.repr_dict = kwargs.get("representation", dict())

    @property
    def values(self):
        """..."""
        return set(self.value_order.keys())

    def is_valid(value):
        """..."""
        value in self.value_order

    def order(self, value):
        """Order to sort.
        You can call this method with both value_type value and string value
        returned by the repr method."""
        if not self._is_valid(value):
            raise ValueError("{} is not a valid value of this parameter."\
                             format(value))
        return self.value_order[value]

    def repr(self, value):
        """..."""
        assert(self.is_valid(value))
        return self.repr_dict.get(value, "{}".format(value))


    @property
    def ordered_values(self):
        """Ordered values 'vs'.

        Parameters
        ------------------------------------------------------------------------
        values :: list
        """
        if vs is None:
            return self.ordered(list(self.values))
        df = pd.DataFrame(values=values, order=[self.order(v) for v in values])\
               .sort(by="order")
        return list(df["values"])

    def random_value(self, n=None):
        """Get n random values.
        Values will be replaced after each choice.

        Return
        ------------------------------------------------------------------------
        value_type #if n is None
        [value_type] #if n is not None
        """
        return np.random.choice(self.values, n)

    def sorted(self, dataframe, ascending=True):
        """dataframe sorted by index that is this Parameter"""
        from dmt.vtk.utils.pandas import sorted
        return sorted(dataframe, order=self.order_dict, level=self.label,
                      ascending=ascending)
        
    def with_index_renamed(self, dataframe, ascending=True):
        """Rename the index of a dataframe."""
        if isinstance(dataframe.index, pd.MultiIndex):
            assert(isinstance(dataframe.index, pd.MultiIndex))
            assert(self.label not in dataframe.index.names)
            
            keys = self.ordered_values
            return flatten([dataframe.xs(k, level=self.label) for k in keys],
                           keys=[self.repr(k) for k in keys], names=[self.label])

        cols = dataframe.columns
        dataframe["order"] = [self.order(v) for v in dataframe.index]
        dataframe.index = pd.Index([self.repr(i) for i in dataframe.index],
                                   dtype="object", name=self.label)
        return dataframe.sort_values(by="order",
                                     ascending=ascending)[cols]
        

    def _filled_multi_index(self, dataframe,
                            sorted=True, ascending=True,
                            with_index_renamed=True):
        """fill in a multi indexed dataframe."""
        index = dataframe.index
        assert(isinstance(index, pd.MultiIndex))
        assert(self.label in dataframe.index.names)

        df_values = level_values(dataframe, level=self.label)
        missing_values = list(self.values - set(df_values))
        if len(missing_values) == 0:
            return (self.with_index_renamed(dataframe) if with_index_renamed
                    else dataframe)

        cols = dataframe.columns
        dfs = [dataframe.xs(v, level=self.label) for v in missing_values]
        mdf = 0.0 * (dfs[0].copy())

        missing_dfs = len(missing) * [mdf.copy()]
        full_df = pd.concat(dfs + missing_dfs,
                            keys=df_values + missing_values,
                            names=[self.label])
        return (self.with_index_renamed(full_df, ascending=ascending)
                if with_index_renamed else full_df)

    def filled(self, dataframe, sorted=True, ascending=True, with_index_renamed=True):
        """Filled and sorted Dataframe by index,
        which is of the type of this Parameter."""
        index = dataframe.index
        if isinstance(index, pd.MultiIndex):
            return self._filled_multi_index(dataframe,
                                            sorted=True,ascending=ascending,
                                            with_index_renamed=with_index_renamed)

        assert(index.name != self.label)
                                                  
        IndexType = type(index)
        missing = list(self.values - set(index))
        missing_df = pd.DataFrame({'mean': len(missing) * [0.],
                                   'std': len(missing) * [0.]})\
                       .set_index(IndexType(missing,
                                            dtype=index.dtype,
                                            name=self.label))
        full_df = pd.concat([dataframe, missing_df])
        #index = pd.Index([self.repr(i) for i in full_df.index],
        #                 dtype="object", name=self.label)
        #print("index {}".format(index))
        #full_df.index = index
        return self.sorted(full_df, ascending=ascending) if sorted else full_df




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

