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
    aggregate_variables = Field(
        __name__ = "aggregate_variables",
        __type__ = tuple, #List[Parameter],#should actually be FiniteValuedParameter, but that causes loopy dependence
        __is_valid_value__ = lambda this, ps: [issubclass(p, Parameter) for p in ps],
        __doc__  = """The (finte-valued) parameter that stands for groups of
        the grouped variable."""
    )
    def __init__(self, aggregate_variables, grouped_variable, *args, **kwargs):
        """..."""
        self.aggregate_variables = aggregate_variables
        self.grouped_variable = grouped_variable

        super(ParameterAggregator, self).__init__(*args, **kwargs)

    @property
    def groups(self):
        """..."""
        def __get_tuples(group_parameters):
            """..."""
            print("get tuples for ", [gp.label for gp in group_parameters])
            if len(group_parameters) == 0:
                return [[]]
            vstail = __get_tuples(group_parameters[1:])
            gphead = group_parameters[0]
            vshead = [[(gphead.label, value)] for value in gphead.values]
            print("head", vshead)
            return [v0 + v1 for v0 in vshead for v1 in vstail]

        return pd.DataFrame([dict(g)
                             for g in __get_tuples(self.aggregate_variables)])

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
        if isinstance(value, self.grouped_variable.value_type):
            return self.grouped_variable.repr(value)
        for aggregate_variable in self.aggregate_variables:
            if isinstance(value, aggregate_variable.value_type):
                return aggregate_variable.repr(value)
            else:
                raise ValueError("{} not an aggregate value, nor grouped."\
                                 .format(value))
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

