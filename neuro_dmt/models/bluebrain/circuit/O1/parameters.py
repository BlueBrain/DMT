"""Parameters used for measurements. """
from abc import abstractmethod
import copy
import numpy as np
import pandas as pd
from bluepy.geometry.roi import ROI
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


class NamedTarget(FiniteValuedParameter):
    """..."""
    value_type = str
    label = "target"
    def __init__(self, *args, **kwargs):
        self.__values = ["mc{}_Column".format(n) for n in range(1, 7)]
        super(NamedTarget, self).__init__(
            value_order = dict(zip(self.__values, range(len(self.__values)))),
            value_repr = dict(zip(self.__values, self.__values)),
            *args, **kwargs
        )
    

class SpatialRandomVariate(ConditionedRandomVariate):
    """A base class to define your spatial random variates.
    Randomly generate position like values in the circuit."""

    def __init__(self, circuit,
                 *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        query :: condition -> dict #that will be sent as a query.
        """
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)

        super(SpatialRandomVariate, self).__init__(*args, **kwargs)


class RandomPosition(SpatialRandomVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self, circuit, offset=50., *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        query :: condition -> dict #that will be sent as a query.
        """
        self.offset = offset

        super(RandomPosition, self).__init__(circuit, *args, **kwargs)

    @abstractmethod
    def query(self, condition, *args, **kwargs):
        pass

    def conditioned_values(self, condition, *args, **kwargs):
        """Generator of positions."""
        bounds = self._helper.geometric_bounds(self.query(condition))
        if bounds is None:
            return ()
        while True:
            yield random_location(Cuboid(bounds.bbox[0] + self.offset,
                                         bounds.bbox[1] - self.offset))


class RandomPositionByCorticalLayer(RandomPosition):
    """..."""
    condition_type = Record(layer=int, target=str)

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(RandomPositionByCorticalLayer, self)\
            .__init__(circuit, *args, **kwargs)

    @classmethod
    def query(cls, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return ({"layer": condition.value.layer, "$target": condition.value.target}
                if condition.value.target else {"layer": condition.value.layer})

class RandomPositionByHippocampalLayer(RandomPosition):
    """..."""
    condition_type = Record(layer=int)
    def __init__(self, circuit, *args, **kwargs):
        """Will use CorticalLayer as conditioning variable.
        Override to use another.

        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super(RandomPositionByHippocampalLayer, self)\
            .__init__(circuit, *args, *kwargs)

    @classmethod
    def query(cls, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return {"layer": condition.layer}
                      

def transform(instance, method_name, function):
    """..."""
    modified_instance = copy.deepcopy(instance)
    method = getattr(instance, method_name)
    def modified_method(*args, **kwargs):
        """Modifed {}""".format(method.__doc__)
        return function(method(instance, *args, **kwargs))

    setattr(modified_instance, method_name, modified_method)


class RandomRegionOfInterest(SpatialRandomVariate):
    value_type = ROI
    def __init__(self, random_position):
        super(RandomRegionOfInterest, self)\
            .__init__(label=random_position.label,
                      condition_type=random_position.condition_type)


def RandomRegionOfInterestByCorticalLayer(circuit,
                                          sample_box_shape=50.*np.ones(3),
                                          *args, **kwargs):
    """..."""
    position = RandomPositionByCorticalLayer(circuit, offset=sample_box_shape,
                                             *args, **kwargs)
    half_box = sample_box_shape / 2.0
    return position.transform(lambda loc: Cuboid(loc - half_box, loc + half_box))

def RandomRegionOfInterestByHippocampalLayer(circuit,
                                             sample_box_shape=50.*np.ones(3),
                                             *args, **kwargs):
    """..."""
    position = RandomPositionByHippocampalLayer(circuit, offset=sample_box_shape,
                                                *args, **kwargs)
    half_box = sample_box_shape / 2.0
    return position.transform(lambda loc: Cuboid(loc - half_box, loc + half_box))
