"""Parameters used for measurements. """
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
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


class RandomRegionOfInterest(ConditionedRandomVariate):
    """Sample random ROIs, conditioned on values of other variables."""
    label = "roi"
    value_type = ROI

    def __init__(self, circuit, *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        keymaker :: condition -> dict #that will be sent as a query.
        """
        self.__logger\
            = Logger("{}Logger".format(self.__class__.__name__),
                     level=kwargs.get("logger_level", Logger.level.PROD))

        assert("conditioning_variables" in kwargs)
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)

        query = kwargs.get("query", None)
        if query:
            self.__class__.query = query
        else:
            self.__logger.warning(
                "No keyword argument 'query'. Expecting subclass to provide."
            )
        super(RandomRegionOfInterest, self).__init__(*args, **kwargs)

    def values(self, condition, *args, **kwargs):
        """..."""
        sampled_box_shape = kwargs.get("sampled_box_shape", 50.*np.ones(3))
        """Generator of ROIs."""
        bounds = self._helper.geometric_bounds(self.query(condition))
        if bounds is None:
            return ()
        half_box = sampled_box_shape / 2.
        region_to_explore = Cuboid(bounds.bbox[0] + half_box,
                                   bounds.bbox[1] - half_box)
        while True:
            loc = random_location(region_to_explore)
            yield Cuboid(loc - half_box, loc + half_box)


class RandomRegionOfInterestByCorticalLayer(RandomRegionOfInterest):
    """Sample random ROIs in a cortical layer."""
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
    def query(cls, condition, target=None):
        """A dict that can be passed to circuit.cells.get(...)"""
        return ({"layer": condition.layer, "$target": target}
                if target else {"layer": condition.layer})


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
