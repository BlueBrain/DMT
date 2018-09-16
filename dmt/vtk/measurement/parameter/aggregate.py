"""Parameter that can aggregate another parameter. """
from abc import abstractmethod
import pandas as pd
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random import RandomParameter
from dmt.vtk.utils.collections import take
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError

class ParameterAggregator:
    """Aggregate a parameter to define another."""
    grouped_variable = Field(
        __name__ = "grouped_variable",
        __type__ = RandomParameter, # <: Parameter
        __doc__  = """The grouped parameter."""
    )
    aggregate_variable = Field(
        __name__ = "aggregate_variable",
        __type__ = Parameter,#should actually be FiniteValuedParameter, but that causes loopy dependence
        __doc__  = """The (finte-valued) parameter that stands for groups of
        the grouped variable."""
    )
    def __init__(self, aggregate_variable, grouped_variable, *args, **kwargs):
        """..."""
        self.aggregate_variable = aggregate_variable
        self.grouped_variable = grouped_variable

        super(ParameterAggregator, self).__init__(*args, **kwargs)

    def random_grouped_values(self, group, *args, **kwargs):
        """A generator of random grouped values.
        Concrete implementation should returned an indexed Pandas DataFrame
        """
        for grouped_value in self.grouped_variable\
                                 .random_values(group, *args, **kwargs):
            yield pd.DataFrame(
                {self.grouped_variable.label: [grouped_value]},
                index=self.index(group)
            )
    def repr(self, value):
        """..."""
        if isinstance(value, self.aggregate_variable.value_type):
            return self.aggregate_variable.repr(value)
        elif isinstance(value, self.grouped_variable.value_type):
            return self.grouped_variable.repr(value)
        else:
            raise ValueError("{} is neither an value of {}, nor of {}"\
                             .format(value, self.aggregate_variable.__class__,
                                     self.grouped_variable.__class__))
        return str(value)

    def index(self, aggregate_values=None, __repr__=True):
        """Index for Pandas DataFrame containing parameter values."""
        if aggregate_values is None:
            aggregate_values = self.aggregate_variable.values
        else:
            if not (isinstance(aggregate_values, list)
                    or isinstance(aggregate_values, tuple) or
                    isinstance(aggregate_values, set)):
                aggregate_values = [aggregate_values,]

                assert(all([self.aggregate_variable.is_valid(v)
                            for v in aggregate_values]))
        return pd.MultiIndex.from_tuples(
            [(self.repr(v) if __repr__ else v,) for v in aggregate_values],
            names=[self.aggregate_variable.label]
        )

    def sample(self, *args, group=None, **kwargs):
        """..."""
        def __sample(group):
            return pd.concat(list(take(
                kwargs.get("size", 20),
                self.random_grouped_values(group=group, *args, **kwargs)
            )))

        if group:
            assert(self.aggregate_variable.is_valid(group))
            return __sample(group)

        return pd.concat([
            __sample(group) for group in self.aggregate_variable.values
        ])

