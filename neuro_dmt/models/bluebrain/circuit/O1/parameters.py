"""Parameters used for measurements.
"""
import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameters import GroupParameter
from dmt.vtk.utils.collections import *
from bluepy.geometry.roi import ROI as RegionOfInterest
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location


class CorticalLayer(GroupParameter):
    """Data and methods associated with cortical layers in a brain region
    circuit."""
    label = "Layer"
    value_type = int
    grouped_variable = Record(__type__ = RegionOfInterest, name = "roi")

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
                                            
        super(CorticalLayer, self).__init__(*args, **kwargs)
        self._values = set([1, 2, 3, 4, 5, 6])

    @property
    def values(self):
        """..."""
        return self._values

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

    def grouped_values(self, layer, *args, **kwargs):
        """All the values of the grouped variable covered by value 'value' of
        this CorticalLayer.
        This is implemented as an infinite stream of randomly generated
        regions of interest in a layer.
        """
        target = kwargs.get("target", None)
        sampled_box_shape = kwargs.get("sampled_box_shape",
                                       np.array([50., 50., 50.]))
        
        q = {"layer": layer, "$target": target} if target else {"layer": layer}
        bounds = self._helper.geometric_bounds(q).bbox
                  
        half_box = sampled_box_shape / 2.0
        region_to_explore = Cuboid(bounds[0] + half_box, bounds[1] - half_box)

        while True:
            loc = random_location(region_to_explore)
            yield Cuboid(loc - half_box, loc + half_box) #or a Cube?

    def __call__(self, *args, **kwargs):
        """Sample ROIS.

        Return
        ------------------------------------------------------------------------
        Generator[(value, RegionOfInterest)]
        """
        n = kwargs.get("sample_size", 20)

        return ((layer, roi)
                for layer in self.values
                for roi in take(n, self.grouped_values(layer, *args, **kwargs)))
