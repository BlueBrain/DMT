"""Base class for Parameter that may assume only one of a few values."""

import copy
import collections
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import ClassAttribute, Field, WithFCA
from dmt.vtk.utils.pandas import flatten, level_values
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random import ConditionedRandomVariate
from dmt.vtk.measurement.condition import ConditionGenerator
from dmt.vtk.utils.logging import Logger, with_logging

@with_logging(Logger.level.STUDY)
class FiniteValuedParameter(
        Parameter):
    """If the number of all possible values of a parameter is finite,
    we can require certain finite data representations of its attributes,
    and adapt Parameter abstractmethods."""

    values = Field(
        __name__ = "values",
        __type__ = list,
        __is_valid__= Field.typecheck.collection("value_type"),
        __doc__="Sorted values assumed by this FiniteValuedParameter.")
    
    value_repr = Field(
        __name__ = "value_repr",
        __type__ = dict,
        __default__={},
        __is_valid__=Field.typecheck.mapping(object, str),
        __doc__="""A dict mapping values to their string representation. You
        may not pass this value to this base class' initializer. There will be
        a default implementation.""")
    
    def __init__(self, value_type, *args, **kwargs):
        """You need to pass a value_type here, and assign it as an attribute.
        This is necessary (as opposed to other fields) because typecheck of
        Field 'values' requires the instance to have this Field assigned.""" 
        self.value_type\
            = value_type
        self._value_order = None
        super().__init__(
            *args, **kwargs)


    @property
    def value_order(self):
        """..."""
        if self._value_order is None:
            self._value_order\
                = dict(zip(
                    self.values, range(len(self.values))))
        return self._value_order

    def is_valid(self, value):
        """..."""
        return value in self.value_order

    def order(self, value):
        """Order to sort.
        You can call this method with both value_type value and string value
        returned by the repr method."""
        if not self.is_valid(value):
            raise ValueError(
                "Received value {} of type {}. Expecting type"\
                .format(value, type(value), self.value_type))
        return self.value_order[value]

    def repr(self, value):
        """..."""
        assert(self.is_valid(value))
        return self.value_repr.get(value, "{}".format(value))

    @property
    def ordered_values(self):
        """Ordered values 'vs'.

        Parameters
        ------------------------------------------------------------------------
        values :: list
        """
        if vs is None:
            return self.ordered(list(self.values))
        dataframe\
            = pd.DataFrame(
                values=values,
                order=[self.order(v) for v in values])\
                .sort(by="order")
        return list(
            dataframe["values"])

    def random_value(self, n=None):
        """Get n random values.
        Values will be replaced after each choice.

        Return
        ------------------------------------------------------------------------
        value_type #if n is None
        [value_type] #if n is not None
        """
        return np.random.choice(self.values, n)

    def sorted(self,
            dataframe,
            ascending=True):
        """dataframe sorted by index that is this Parameter"""
        from dmt.vtk.utils.pandas import sorted
        return sorted(dataframe, order=lambda v: self.value_order[v],
                      level=self.label, ascending=ascending)
        
    def repr_index(self,
            dataframe,
            ascending=True):
        """Rename the index of a dataframe."""
        if isinstance(dataframe.index, pd.MultiIndex):
            #not tested yet
            assert(isinstance(dataframe.index, pd.MultiIndex))
            assert(self.label not in dataframe.index.names)
            
            keys = self.ordered_values
            return flatten([dataframe.xs(k, level=self.label) for k in keys],
                           keys=[self.repr(k) for k in keys], names=[self.label])

        assert dataframe.index.name == self.label
        new_index = pd.Index([self.repr(i) for i in dataframe.index],
                             name=dataframe.index.name)
        return dataframe.set_index(new_index)

    def _filled_multi_index(self,
            dataframe,
            *args, **kwargs):
        """fill in a multi indexed dataframe."""
        index = dataframe.index
        assert(isinstance(index, pd.MultiIndex))
        assert(self.label in dataframe.index.names)

        df_values = level_values(dataframe, level=self.label)
        missing_values = list(set(self.values) - set(df_values))
        if len(missing_values) == 0:
            return dataframe

        cols = dataframe.columns
        dfs = [dataframe.xs(v, level=self.label) for v in missing_values]
        mdf = 0.0 * (dfs[0].copy())

        missing_dfs = len(missing) * [mdf.copy()]
        return pd.concat(
            dfs + missing_dfs,
            keys=df_values + missing_values,
            names=[self.label])

    def filled(self,
            dataframe,
            sorted=True,
            ascending=True,
            with_index_renamed=True):
        """Filled and sorted Dataframe by index,
        which is of the type of this Parameter."""
        self.logger.debug("measurement has an index of type {}"\
                          .format(type(dataframe.index)))
        if isinstance(dataframe.index, pd.MultiIndex):
            return\
                self._filled_multi_index(
                    dataframe,
                    sorted=True,
                    ascending=ascending,
                    with_index_renamed=with_index_renamed)
        if dataframe.index.name != self.label:
            raise ValueError("index name {} != self.label {}"\
                             .format(dataframe.index.name, self.label))
                                                  
        IndexType = type(dataframe.index)
        missing = list(set(self.values) - set(dataframe.index))
        self.logger.debug("missing values in the index {}".format(missing))
        missing_df=\
            pd.DataFrame(
                len(missing) * [[0., 0.]],
                index=IndexType(
                    missing,
                    name=dataframe.index.name),
                columns=dataframe.columns)
        self.logger.debug("missing data frame {}".format(missing_df))
        self.logger.debug("dataframe measured {}".format(dataframe))
        full_df = pd.concat([dataframe, missing_df])
        return self.sorted(full_df, ascending=ascending) if sorted else full_df

    def make_aggregator(self, rand_var_gen_func):
        """This 'FiniteValuedParameter' as an aggregator of 'grouped_variable.
        The grouped variable must be of the following form:

        Parameters
        ------------------------------------------------------------------------
        ran_var_gen_func :: FunctionType # a generator function that generates
        ~                                # random values under a given condition.
        """
        @classmethod
        def conditioned_values(cls, condition, *args, **kwargs):
            """..."""
            return rand_var_gen_func(condition, *args, **kwargs)

        T = type("{}ConditionedRandomVariate".format(self.__class__.__name),
                 (ConditionedRandomVariate,),
                 {"conditioned_values": conditioned_values})

        return T(conditions=(self,))
