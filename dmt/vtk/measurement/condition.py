"""Measurement can be made under given conditions."""

import pandas as pd
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup


class Condition:
    """Collection of fields that together condition a statistical measurement."""
    def __init__(self,
            param_value_pairs,
            *args, **kwargs):
        """..."""
        self.__param_value_pairs\
            = sorted(
                [(self.__get_label(param), value)
                 for param, value in param_value_pairs],
                key=lambda key_value: key_value[0])
        self.__record\
            = Record(
                **{param: value
                   for param, value in self.__param_value_pairs})
        super().__init__(*args, **kwargs)


    @property
    def as_dict(self):
        """..."""
        return self.__record.as_dict

    @property
    def hash_id(self):
        """dict does not use __hash___!"""
        return self.__hash__()

    def __hash__(self):
        """Convert this Condition to a string and hash it."""
        return hash(str(self.__param_value_pairs))

    @classmethod
    def __get_label(cls, param):
        """..."""
        try:
            return param.label
        except AttributeError:
            return param

    def __contains__(self, key):
        """..."""
        return self.__get_label(key) in self.__record

    def specifies(self, parameter):
        """Does condition specify a value for parameter 'key'?"""

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
        return pd.MultiIndex.from_tuples([
            tuple(value for _, value in self.__param_value_pairs)],
            names=[param for param, _ in self.__param_value_pairs])

    def is_valid(self, value):
        """..."""
        return all(
            hasattr(value, field)
            for field in self.fields)

    def plus(self, param_value_pairs):
        """..."""
        return Condition(
            self.__param_value_pairs +
            [(self.__get_label(param), value)
             for param, value in param_value_pairs])

class ConditionGenerator(
        ParameterGroup):
    """a minor extension."""

    def __init__(self, arg0, *args, **kwargs):
        """
        Arguments
        ---------------------
        arg0 : either a 'Parameter' or a List[Parameter]
        args : sequence of Parameters
        ---------------------
        If arg0 is a list, only this list's elements will be used, and
        arg1 ignored.
        """
        self.__conditioning_variables=\
            ({v.label: v for v in arg0}
             if collections.check(arg0) else
             dict([(arg0.label, arg0)] +
                  [(arg.label, arg) for arg in args]))
        super().__init__(
            arg0,
            *args, **kwargs)
            
    @property
    def conditioning_variables(self):
        """..."""
        return self.parameters

    def value_type(self, label):
        """Types of parameters' values."""
        return self.__conditioning_variables[label].value_type

    def __iter__(self):
        for d in self.kwargs:
            yield Condition([
                (param, d[param.label]) for param in self.parameters ])

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
            return size * tuple(condition.value.get(variable.label)
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


