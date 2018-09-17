"""Parameter that can aggregate another parameter. """
from abc import abstractmethod
import pandas as pd
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random import RandomVariate
from dmt.vtk.utils.collections import take, Record
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError


class ParameterAggregator:
    """Aggregate a parameter to define another."""
    grouped_variable = Field(
        __name__ = "grouped_variable",
        __type__ = RandomVariate, 
        __doc__  = """The grouped parameter."""
    )
    aggregate_variables = Field(
        __name__ = "aggregate_variables",
        __type__ = tuple, #List[Parameter],#should actually be FiniteValuedParameter, but that causes loopy dependence
        __is_valid_value__ = lambda this, ps: all(issubclass(p, Parameter) for p in ps),
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
            if len(group_parameters) == 0:
                return [[]]
            vstail = __get_tuples(group_parameters[1:])
            gphead = group_parameters[0]
            vshead = [[(gphead.label, value)] for value in gphead.values]
            return [v0 + v1 for v0 in vshead for v1 in vstail]

        for g in __get_tuples(self.aggregate_variables):
            yield Record(**dict(g))

    def random_grouped_values(self, group, *args, **kwargs):
        """A generator of random grouped values.
        Concrete implementation should returned an indexed Pandas DataFrame
        """
        rgvs = take(kwargs.get("size", 20),
                    self.grouped_variable.random_values(group, *args, **kwargs))
        for grouped_value in rgvs:
            yield pd.DataFrame(
                {self.grouped_variable.label: [grouped_value]},
                index=self.index([group])
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

    def index(self, groups=None, __repr__=True):
        """Index for the Pandas DataFrame containing parameter values."""
        if groups is None:
            groups = self.groups

        groups_as_dict = [g.as_dict for g in groups]

        variables = [v.label for v in self.aggregate_variables]
        group_tuples = [tuple(getattr(g, v) for v in variables) for g in groups]

        return pd.MultiIndex.from_tuples(group_tuples, names=variables)

    def sample(self, *args, group=None, **kwargs):
        """..."""
        def __sample(group):
            return pd.concat(list(take(
                kwargs.get("size", 20),
                self.random_grouped_values(group=group, *args, **kwargs)
            )))

        if group:
            return __sample(group)

        return pd.concat([__sample(group) for group in self.groups])

