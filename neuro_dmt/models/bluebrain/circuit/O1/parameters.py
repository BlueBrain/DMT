"""Parameters used for measurements.
"""
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate
from dmt.vtk.measurement.parameter.group import \
    GroupParameter, ParameterAggregator
from dmt.vtk.utils.collections import *
from dmt.vtk.utils.descriptor import ClassAttribute, Field
from bluepy.geometry.roi import ROI
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.measurement.parameter import \
    Layer, CorticalLayer, HippocampalLayer


class RegionOfInterest(RandomVariate):
    """Region of interest formalized as a measurement.Parameter."""

    label = "roi"

    value_type = ROI

    def __init__(self, *args, **kwargs):
        """..."""
        assert("circuit" in kwargs)
        self._circuit = kwargs["circuit"]
        self._helper = BlueBrainModelHelper(circuit=self._circuit)

    def values(self, query, *args, **kwargs):
        sampled_box_shape = kwargs.get("sampled_box_shape", 50.*np.ones(3))
        """Generator of ROIs."""
        bounds = self._helper.geometric_bounds(query)
        if bounds is None:
            return ()
        half_box = sampled_box_shape / 2.
        region_to_explore = Cuboid(bounds.bbox[0] + half_box,
                                   bounds.bbox[1] - half_box)
        while True:
            loc = random_location(region_to_explore)
            yield Cuboid(loc - half_box, loc + half_box)


class LayerROIs(ParameterAggregator):
    """..."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        self.aggregate = 

    @abstractmethod
    def query(self, layer, target=None):
        """A dict that can be passed to circuit.cells.get(...)"""
        return \
            {"layer": layer, "$target": target} if target else {"layer": layer}

    def random_grouped_values(self, layer, *args, **kwargs):
        """..."""
        target=kwargs.get("target", None)
        query = self.query(layer, target=target)
                                          
        for roi in self._grouped.values(query, *args, **kwargs):
            yield pd.DataFrame({self._grouped.label: [roi]},
                               index=self.index(layer))


class CorticalLayerROIs(LayerROIs):
    """Aggregates ROIs in cortical layers."""
    LayerType = CorticalLayer
                 
    def query(self, layer, target=None):
        """A dict that can be passed to circuit.cells.get(...)"""
        return \
            {"layer": layer, "$target": target} if target else {"layer": layer}

class HippocampalLayerROIs(LayerROIs):
    """Aggregates ROIs in hippocampal layers."""
    LayerType = HippocampalLayer

    def query(self, layer):
        """A dict that can be passed to circuit.cells.get(...)"""
        return {"layer": layer}
