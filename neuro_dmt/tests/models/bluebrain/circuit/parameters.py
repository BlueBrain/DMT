"""Test develop Blue Brain circuit parameters."""

import numpy as np
from bluepy.v2.circuit import Circuit
from bluepy.geometry.roi import ROI
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random import \
    RandomVariate, ConditionedRandomVariate, get_conditioned_random_variate
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.models.bluebrain.circuit.parameters \
    import PreMtype, PostMtype, Pathway
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, random_location
from neuro_dmt.measurement.parameter import CorticalLayer

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

#mtype_pre = PreMtype(circuit)
#mtype_post = PostMtype(circuit)

#syn_count = StatisticalMeasurement(method=PairSynapseCount(circuit),
#                                   by=[mtype_pre, mtype_post])



cl = CorticalLayer()

class BBCorticalLayerROIs(ConditionedRandomVariate):
    label = "roi"
    value_type = ROI
    def __init__(self, *args, **kwargs):
        self._circuit = kwargs["circuit"]
        self._helper  = BlueBrainModelHelper(circuit=circuit)
        super(BBCorticalLayerROIs, self).__init__(*args, **kwargs)

    def query(self, condition):
        """..."""
        return {'layer': condition.layer}

    def values(self, condition, *args, **kwargs):
        """..."""
        sampled_box_shape = kwargs.get("sampled_box_shape", 50.*np.ones(3))
        bounds = self._helper.geometric_bounds(self.query(condition))
        if bounds is None:
            return ()
        half_box = sampled_box_shape / 2.
        region_to_explore = Cuboid(bounds.bbox[0] + half_box,
                                   bounds.bbox[1] - half_box)
        while True:
            loc = random_location(region_to_explore)
            yield Cuboid(loc - half_box, loc + half_box)

bbcl = BBCorticalLayerROIs(circuit=circuit, conditioning_variables=(cl,))

#bblcrv = get_conditioned_random_variate((cl,), bbcl, circuit=circuit)





