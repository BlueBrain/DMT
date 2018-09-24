"""Measurement can be made under given conditions."""

import collections
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup


class Condition:
    """Collection of fields that together condition a statistical measurement."""
    def __init__(self, param_value_pairs):
        """..."""
        self.__param_value_pairs = param_value_pairs
        self.__record = Record(**{param.label: value
                                  for param, value in param_value_pairs})

    @property
    def value(self):
        """..."""
        return self.__record

    def get_value(self, label):
        """..."""
        return self.__record.get(label)

    @property
    def fields(self):
        """..."""
        return self.__record.fields

    @property
    def index(self):
        """A Pandas Index object."""
        return pd.MultiIndex.from_tuples(
            [tuple(param.repr(value) for param, value in self.__param_value_pairs)],
            names=[param.label for param, _ in self.__param_value_pairs]
        )

    def is_valid(self, value):
        """..."""
        return all(hasattr(value, field) for field in self.fields)


class ConditionGenerator(ParameterGroup):
    """a minor extension."""

    def __init__(self, arg0, *args, **kwargs):
        """..."""
        self.__conditioning_variables = (
            {v.label: v for v in arg0}
            if isinstance(arg0,  collections.Iterable) else
            dict([(arg0.label, arg0)] + [(arg.label, arg) for arg in args])
        )
        super(ConditionGenerator, self).__init__(arg0, *args, **kwargs)
            
    @property
    def conditioning_variables(self):
        """..."""
        return self.parameters

    def value_type(self, label):
        """Types of parameters' values."""
        return self.__conditioning_variables[label].value_type

    def __iter__(self):
        for d in self.kwargs:
            yield Condition([(param, d[param.label]) for param in self.parameters])

    @property
    def values(self):
        """..."""
        return pd.DataFrame([x for x in self])

    def index(self, conditions=None, size=20):
        """..."""
        if not conditions:
            conditions = self
        def __tuple(condition):
            """..."""
            return size * tuple(variable.repr(condition.value.get(variable.label))
                                for variable in self.conditioning_variables)
        return pd.MultiIndex.from_tuples([__tuple(c) for c in conditions],
                                         names=self.labels)


def get_conditions(arg0, *args):
    """conditions for variables
    You may pass an argument sequence,

    get_conditions(cortical_layer, hypercolumn, mtype)....
    ----------------------------------------------------------------------------
    or you may pass a single argument,
    get_conditions((cortical_layer, hypercolumn, mtype))


    Parameters
    ----------------------------------------------------------------------------
    args :: Either[ArgSeq[Parameter], List[Parameter]]
    """
    variables\
        = arg0 if isinstance(arg0, collections.Iterable) else [arg0] + args

    return ParameterGroup(variables).kwargs


