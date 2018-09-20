"""A parameter like that groups another parameter"""

from abc import abstractmethod
import collections
import pandas as pd
from dmt.vtk.measurement.parameter import Parameter
#from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.utils.collections import take, Record
from dmt.vtk.utils.descriptor import ClassAttribute


class ParameterGroup:
    """A group of parameters."""

    def __init__(self, arg0, *args, **kwargs):
        """...

        Parameters
        ------------------------------------------------------------------------
        parameters :: Iterable(FiniteValuedParameter)
        """
        self.__parameters = (
            arg0 if isinstance(arg0, collections.Iterable)
            else (arg0,) + args
        )

    @property
    def parameters(self):
        """..."""
        return self.__parameters

    @property
    def kwargs(self):
        """A dict that can be used as keyword arguments for a function."""
        def __get_tuple_values(params):
            """..."""
            if not params:
                return [[]]
            head_tuples = [[(params[0].label, v)] for v in params[0].values]
            tail_tuples = __get_tuple_values(params[1:])
            return [h+t for h in head_tuples for t in tail_tuples]

        for param_values in __get_tuple_values(self.parameters):
            yield dict(param_values)


class Grouper:
    """A parameter that groups another. For example in a brain,
    Layer is a parameter that groups positions in a brain region.
    """
    grouped_variable = ClassAttribute(
        __name__ = "grouped_variable",
        __type__ = Record,
        __is_valid_value__ = (
            lambda r: hasattr(r, '__type__') and hasattr(r, 'name')
        ),
        __doc__  = """Metadata for the variable grouped by this GroupParameter."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        super(Group, self).__init__(*args, **kwargs)

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


#some relevant methods as well
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
