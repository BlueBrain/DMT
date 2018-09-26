"""Parameters used for measurements. """
from abc import ABC, abstractmethod
import collections
import copy
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate
from dmt.vtk.utils.collections import *
from dmt.vtk.utils.descriptor import ClassAttribute, Field
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.random_variate import \
    BrainRegionSpecific


    
def transform(instance, method_name, mapping):
    """..."""
    modified_instance = copy.deepcopy(instance)
    method = getattr(instance, method_name)
    def modified_method(*args, **kwargs):
        """Modifed {}""".format(method.__doc__)
        x = method(instance, *args, **kwargs)
        if isinstance(x, collections.Iterable):
            for y in x:
                yield mapping(y)
        else:
            return mapping(x)

    setattr(modified_instance, method_name, modified_method)
    return modified_instance
