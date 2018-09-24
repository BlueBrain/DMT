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
from neuro_dmt.measurement.parameter import \
    Layer, CorticalLayer, HippocampalLayer
from neuro_dmt.models.bluebrain.circuit.parameters import \
    NamedTarget, \
    RandomPosition, \
    RandomRegionOfInterest, \
    RandomBoxCorners, \
    BrainRegionSpecific


class Cortical(BrainRegionSpecific):
    """..."""
    region_label = "cortical"

    def __init__(self, by=tuple(), target="mc2_Column", *args, **kwargs):
        """..."""
        cell_group_params = by if by else ("layer", "$target")
        super(Cortical, self).__init__(cell_group_params, target=target,
                                       *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {p: condition.get_value(p) for p in self.cell_group_params}


class Hippocampal(BrainRegionSpecific):
    """..."""
    region_label = "hippocampal"

    def __init__(self, by=None, *args, **kwargs):
        """..."""
        cell_group_params = by if by else ("layer",)
        super(Hippocampal, self).__init__(cell_group_params, *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {p: condition.get_value(p) for p in self.cell_group_params}

    
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


def get_cortical_roi(circuit,
                     sample_box_shape=50.*np.ones(3),
                     *args, **kwargs):
    """..."""
    position = CorticalRandomPosition(circuit, offset=sample_box_shape,
                                      *args, **kwargs)
    half_box = sample_box_shape / 2.0
    return position.transform(
        Record(label="roi",
               function=lambda loc: Cuboid(loc - half_box, loc + half_box))
    )

def get_hippocampal_roi(circuit,
                        sample_box_shape=50.*np.ones(3),
                        *args, **kwargs):
    """..."""
    position = HippocampalRandomPosition(circuit, offset=sample_box_shape,
                                         *args, **kwargs)
    half_box = sample_box_shape / 2.0
    return position.transform(
        Record(label="roi",
               function=lambda loc: Cuboid(loc - half_box, loc + half_box))
    )


