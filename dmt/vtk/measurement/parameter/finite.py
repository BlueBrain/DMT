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
class FiniteValuedParameter(Parameter, WithFCA):
    """If the number of all possible values of a parameter is finite,
    we can require certain finite data representations of its attributes,
    and adapt Parameter abstractmethods."""
    value_order = Field(
        __name__ = "value_order",
        __type__ = dict, 
        __is_valid_value__ = lambda self, value_order_dict: all(
            (isinstance(value, self.value_type) and
             isinstance(order, int) and order >= 0)
            for value, order in value_order_dict.items()
        ),
        __doc__="""A dict mapping values to their order.""" 
    )
    value_repr = Field(
        __name__ = "value_repr",
        __type__ = dict,
        __is_valid_value__ = lambda self, vrdict: all(
            isinstance(value, self.value_type) and isinstance(rep, str)
            for value, rep in vrdict.items()
        ),
        __doc__="""A dict mapping values to their string representation. You
        may not pass this value to this base class' initializer. There will be
        a default implementation."""
    )
    def __init__(self, values=None, *args, **kwargs):
        """..."""
        super(FiniteValuedParameter, self).__init__(*args, **kwargs)

        self._values_assumed = set(self.value_order.keys())
        if values:
            if not isinstance(values, set):
                self.logger.alert(
                    """{} passed as argument 'values' which should be a set.
                    Will make it a set and proceed""".format(values)
                )
                values = set(values)
            for v in values.difference(self._values_assumed):
                self.logger.warn(
                    """Parameter {} does not assume a value of {},
                    and will be skipped""".format(self.__class__.__name__, v)
                )
            self._values_assumed = self._values_assumed.intersection(values)
            
    @property
    def values(self):
        """..."""
        return self._values_assumed

    def is_valid(self, value):
        """..."""
        return value in self.value_order

    def order(self, value):
        """Order to sort.
        You can call this method with both value_type value and string value
        returned by the repr method."""
        if not self.is_valid(value):
            raise ValueError("Received value {} of type {}. Expecting type"\
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
        return sorted(dataframe, order=lambda v: self.value_order[v],
                      level=self.label, ascending=ascending)
        
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

    def filled(self, dataframe,
               sorted=True, ascending=True,
               with_index_renamed=True):
        """Filled and sorted Dataframe by index,
        which is of the type of this Parameter."""
        self.logger.debug("measurement has an index of type {}"\
                          .format(type(dataframe.index)))
        if isinstance(dataframe.index, pd.MultiIndex):
            return self._filled_multi_index(dataframe,
                                            sorted=True,ascending=ascending,
                                            with_index_renamed=with_index_renamed)
        if dataframe.index.name != self.label:
            raise ValueError("index name {} != self.label {}"\
                             .format(dataframe.index.name, self.label))
                                                  
        IndexType = type(dataframe.index)
        missing = list(self.values - set(dataframe.index))
        self.logger.debug("missing values in the index {}".format(missing))
        missing_df = pd.DataFrame(len(missing) * [[0., 0.]],
                                  index=IndexType(missing,
                                                  name=dataframe.index.name),
                                  columns=dataframe.columns)
        self.logger.debug("missing data frame {}".format(missing_df))
        self.logger.debug("dataframe measured {}".format(dataframe))
        full_df = pd.concat([dataframe, missing_df])
        #index = pd.Index([self.repr(i) for i in full_df.index],
        #                 dtype="object", name=self.label)
        #print("index {}".format(index))
        #full_df.index = index
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
