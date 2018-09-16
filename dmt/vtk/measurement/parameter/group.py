"""A parameter like that groups another parameter"""

from abc import abstractmethod
import pandas as pd
from dmt.vtk.measurement.parameter.generator import ParamGenerator
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.utils.collections import take, Record
from dmt.vtk.utils.descriptor import ClassAttribute


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
               for v in p0.aggregate_variable.values
               for gv in take(n, p0.random_grouped_values(v, *args, **kwargs))]
        if index + 1 == len(group_params):
            return vs0
        else:
            vsrest = __get_tuples(index + 1)
            return [v0 + v1 for v0 in vs0 for v1 in vsrest]

    return pd.DataFrame([dict(t) for t in __get_tuples(0)])
