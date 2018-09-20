"""Parameters used for measurements. """
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate
from dmt.vtk.utils.collections import *
from dmt.vtk.utils.descriptor import ClassAttribute, Field
from dmt.vtk.utils.logging import Logger
from bluepy.geometry.roi import ROI
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.measurement.parameter import \
    Layer, CorticalLayer, HippocampalLayer

class SpatialRandomVariate(ConditionedRandomVariate):
    """A base class to define your spatial random variates.
    Randomly generate position like values in the circuit."""

    def __init__(self, circuit,
                 log_level=Logger.level.PROD,
                 *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        query :: condition -> dict #that will be sent as a query.
        """
        assert("conditioning_variables" in kwargs)
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        self._log_level = log_level

        super(SpatialRandomVariate, self).__init__(*args, **kwargs)

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = Logger("{}Logger".format(self.__class__.__name__),
                                  level=getattr(self, "_log_level",
                                                Logger.level.PROD))
        return self._logger
         

class RandomPosiion(SpatialRandomVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self, circuit, query=None, offset=50., *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        query :: condition -> dict #that will be sent as a query.
        """
        if query:
            self.__class__.query = query
        else:
            self.logger.warning(
                "No keyword argument 'query'. Expecting subclass to provide."
            )

        self.offset = offset

        super(RandomPosiion, self).__init__(circuit, *args, **kwargs)

    def values(self, condition, *args, **kwargs):
        """Generator of positions."""
        bounds = self._helper.geometric_bounds(self.query(condition))
        if bounds is None:
            return ()
        while True:
            yield random_location(Cuboid(bounds.bbox[0] + offset,
                                         bounds.bbox[1] - offset))


class RandomRegionOfInterest(SpatialRandomVariate):
    """Convert a randomly generated position into an ROI."""
    def __init__(self, circuit, query=None,
                 sampled_box_shape=50.*np.ones(3),
                 *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        query :: condition -> dict #that will be sent as a query.
        """
        self.half_box = sampled_box_shape / 2.
        self.random_position = RandomPosiion(circuit, query=query,
                                             offset=self.half_box,
                                             *args, **kwargs)
        super(RandomRegionOfInterest, self).__init__(circuit, *args, **kwargs)

    def values(self, condition, *args, **kwargs):
        """Generator of ROIs"""
        for position in self.random_position.values(condition, *args, **kwargs):
            yield Cuboid(loc - self.half_box, loc + self.half_box)


class RandomRegionOfInterestByCorticalLayer(RandomRegionOfInterest):
    """Sample random ROIs in a cortical layer."""

    condition_type = Record(layer=int, target=str)
    def __init__(self, circuit, *args, **kwargs):
        """Will use CorticalLayer as conditioning variable.
        Override to use another.

        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super(RandomRegionOfInterestByCorticalLayer, self)\
            .__init__(circuit, conditioning_variables=(CorticalLayer(),),
                      *args, *kwargs)

    @classmethod
    def query(cls, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return ({"layer": condition.layer, "$target": condition.target}
                if condition.target else {"layer": condition.layer})


class RandomRegionOfInterestByHippocampalLayer(RandomRegionOfInterest):
    """Aggregates ROIs in hippocampal layers."""
    def __init__(self, circuit, *args, **kwargs):
        """Will use CorticalLayer as conditioning variable.
        Override to use another.

        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super(RandomRegionOfInterestByCorticalLayer, self)\
            .__init__(circuit, conditioning_variables=(HippocampalLayer(),),
                      *args, *kwargs)

    @classmethod
    def query(cls, condition):
        """A dict that can be passed to circuit.cells.get(...)"""
        return {"layer": condition.layer}


