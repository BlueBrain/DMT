"""Parameters used for measurements.
"""
from abc import abstractmethod
import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameters import GroupParameter
from dmt.vtk.utils.collections import *
from bluepy.geometry.roi import ROI as RegionOfInterest
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location


class Layer(GroupParameter):
    """A generic layer in any brain region."""
    label = "Layer"
    grouped_variable = Record(__type__=RegionOfInterest, name="roi")

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)


        super(Layer, self).__init__(*args, **kwargs)

    @property
    def values(self):
        """..."""
        return self._values

    @abstractmethod
    def query(self, layer):
        """Query to be used by bluepy"""
        pass

    def random_grouped_values(self, layer, *args, **kwargs):
        """All the values of the grouped variable covered by value 'value' of
        this CorticalLayer.
        This is implemented as an infinite stream of randomly generated
        regions of interest in a layer.
        """
        target = kwargs.get("target", None)
        sampled_box_shape = kwargs.get("sampled_box_shape",
                                       np.array([50., 50., 50.]))
        q = self.query(layer, target=target)
        bounds = self._helper.geometric_bounds(q)
        if bounds is None:
            return []
                  
        half_box = sampled_box_shape / 2.0
        region_to_explore = Cuboid(bounds.bbox[0] + half_box,
                                   bounds.bbox[1] - half_box)

        while True:
            loc = random_location(region_to_explore)
            yield Cuboid(loc - half_box, loc + half_box) #or a Cube?


class CorticalLayer(Layer):
    """Data and methods associated with cortical layers in a brain region
    circuit."""
    value_type = int
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(CorticalLayer, self).__init__(circuit, *args, **kwargs)
        self._values = set([1, 2, 3, 4, 5, 6])

    def is_valid(self, value):
        """Is 'value' a valid value?"""
        return value > 0 and value < 7

    def order(self, value):
        """Order of value."""
        return value

    def repr(self, value):
        """Represent value 'value'"""
        if not self.is_valid(value):
            raise ValueError("{} is not a valid value of {}"\
                             .format(self.value, self.__class__))
        return {
            1: "I",
            2: "II",
            3: "III",
            4: "IV",
            5: "V",
            6: "VI"
        }[value]

    def query(self, layer, target=None):
         return ({"layer": layer, "$target": target}
                 if target else {"layer": layer})


class HippocampalLayer(Layer):
    value_type = str
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        super(HippocampalLayer, self).__init__(circuit, *args, **kwargs)
        self._values = set(["SLM", "SR", "SP", "SO"])

    def is_valid(self, value):
        """..."""
        return value in self._values

    def repr(self, value):
        """..."""
        return value

    def order(self, value):
        """..."""
        return dict(SLM=0, SR=1, SP=2, SO=3)[value]

    def query(self, layer, target=None):
         return ({"layer": layer, "$target": target}
                 if target else {"layer": layer})
