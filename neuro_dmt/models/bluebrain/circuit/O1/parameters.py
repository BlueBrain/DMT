"""Parameters used for measurements.
"""
from abc import abstractmethod
import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameters import Parameter, GroupParameter
from dmt.vtk.utils.collections import *
from bluepy.geometry.roi import ROI
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.measurement.parameter import CorticalLayer, HippocampalLayer


class RegionOfInterest(Parameter):
    """Region of interest formalized as a measurement.Parameter."""

    label = "roi"

    value_type = ROI

    def __init__(self, *args, **kwargs):
        """..."""
        assert("circuit" in kwargs)
        self._circuit = kwargs["circuit"]
        self._helper = BlueBrainModelHelper(circuit=self._circuit)

    def values(self, query, sampled_box_shape=50.*np.ones(3)):
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


class BBO1Layer(GroupParameter):
    """A generic layer in any brain region."""
    grouped_variable = Record(__type__ = RegionOfInterest, name = "roi")

    def __init__(self, *args, **kwargs):
        """..."""
        assert("circuit" in kwargs)
        self._circuit = kwargs["circuit"]
        self._helper = BlueBrainModelHelper(circuit=self._circuit)
        super(BBO1Layer, self).__init__(*args, **kwargs)

    @abstractmethod
    def query(self, layer, target=None):
        """Query to be used by bluepy"""
        pass

    def random_grouped_values(self, layer, *args, **kwargs):
        target = kwargs.get("target", None)
        sampled_box_shape = kwargs.get("sampled_box_shape",
                                        np.array([50., 50., 50.]))
        return RegionOfInterest(circuit=self._circuit).values(
            self.query(layer, target=target),
            sampled_box_shape = sampled_box_shape
        )
        

class BBO1CorticalLayer(CorticalLayer, BBO1Layer):
    """Data and methods associated with cortical layers in a brain region
    circuit."""
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        kwargs.update({"circuit": circuit})
        super(BBO1CorticalLayer, self).__init__(*args, **kwargs)

    def query(self, layer, target=None):
         return ({"layer": layer, "$target": target}
                 if target else {"layer": layer})


class BBO1HippocampalLayer(CorticalLayer, BBO1Layer):
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        kwargs.update({"circuit": circuit})
        super(BBO1HippocampalLayer, self).__init__(*args, **kwargs)

    def query(self, layer, target=None):
         return ({"layer": layer, "$target": target}
                 if target else {"layer": layer})
