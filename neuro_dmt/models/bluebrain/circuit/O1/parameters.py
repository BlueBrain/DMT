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
    sub_region_label = "layer"
    condition_type = Record(layer=int)
    def cell_query(self, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return {self.sub_region_label: condition.value.get(self.sub_region_label)}


class Hippocampal(BrainRegionSpecific):
    """..."""
    region_label = "hippocampal"
    sub_region_label = "layer"
    condition_type = Record(layer=int)
    @classmethod
    def cell_query(cls, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return {"layer": condition.layer}


class CorticalRandomPosition(Cortical, RandomPosition):
    """..."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(CorticalRandomPosition, self)\
            .__init__(circuit, *args, **kwargs)
            

class CorticalRandomPositionByLayer(RandomPosition):
    """..."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(CorticalRandomPositionByLayer, self)\
            .__init__(circuit,
                      brain_region=Cortical("layer"),
                      *args, **kwargs)

#just an example, remove!
def cortical_random_positions_by_layer(circuit, offset=50, *args, **kwargs):
    """..."""
    return RandomPosition(circuit, Cortical("layer"), offset=offset,
                          *args, **kwargs)
    

class HippocampalRandomPosition(Hippocampal, RandomPosition):
    """..."""
    condition_type = Record(layer=int)
    def __init__(self, circuit, *args, **kwargs):
        """Will use CorticalLayer as conditioning variable.
        Override to use another.

        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super(HippocampalRandomPosition, self).__init__(circuit, *args, *kwargs)
            

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


class CorticalRandomRegionOfInterest(Cortical, RandomRegionOfInterest):
    """..."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(CorticalRandomRegionOfInterest, self)\
            .__init__(circuit, *args, **kwargs)


class CorticalRandomBoxCorners(Cortical, RandomBoxCorners):
    """..."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(CorticalRandomBoxCorners, self)\
            .__init__(circuit, *args, **kwargs)


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


