"""Test cell density measurement."""

import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.models.bluebrain import BlueBrainModelHelper, geometry
from neuro_dmt.models.bluebrain.geometry import Cuboid
from neuro_dmt.models.bluebrain.measurements.circuit.composition \
    import CellDensityMeasurement

def sample_region_of_interest(circuit, target='mc2_Column',
                              sampled_box_shape=np.array([50., 50., 50.]),
                              sample_size = 10):
    """Get a generator of regions of interest.
    
    Return
    ------------------------------------------------------------------------
    Layer -> Generator[RegionOfInterest] #Layer == int
    """
    helper = BlueBrainModelHelper(circuit=circuit, target=target)

    def _get_region_to_explore(layer):
        """..."""
        layer_bounds = helper.geometric_bounds({'layer': layer})
        p0, p1 = layer_bounds.bbox
        return Cuboid(p0 + sampled_box_shape,
                      p1 - sampled_box_shape)
    
    def roi_sampler(layer):
        """..."""
        def get_roi(loc):
            half_box = sampled_box_shape / 2.
            return Cuboid(loc - half_box, loc + half_box)
        return (get_roi(geometry.random_location(_get_region_to_explore(layer)))
                for _ in range(sample_size))
    
    return roi_sampler



layer_groups = Record(label = "layer",
                      values = [1,2,3,4,5,6])



cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)
cd = CellDensityMeasurement(circuit)

roi_sampler = Record(group=layer_groups,
                     sample=sample_region_of_interest(circuit))
cds = cd.statistical_measurement(roi_sampler)
