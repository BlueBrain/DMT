"""Measurement can be made under given conditions."""

import collections
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup


class Condition:
    """Collection of fields that together condition a statistical measurement."""
    def __init__(self, **kwargs):
        """..."""
        self.value = Record(**kwargs)

    @property
    def fields(self):
        """..."""
        return self.value.fields

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
    def labels(self):
        """..."""
        return tuple(l for l in self.__conditioning_variables.keys())

    @property
    def conditioning_variables(self):
        """..."""
        return tuple(self.__conditioning_variables[l] for l in self.labels)

    @property
    def value_type(self, label):
        """Types of parameters' values."""
        return self.__conditioning_variables[label].value_type

    def __iter__(self):
        return self.kwargs

    @property
    def values(self):
        """..."""
        return pd.DataFrame([x for x in self])

    def index(self, conditions=None):
        """..."""
        if not conditions:
            conditions = self
        def __tuple(condition):
            """..."""
            return tuple(variable.repr(condition[variable.label])
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


