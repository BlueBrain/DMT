"""Test develop Blue Brain circuit parameters."""

import numpy as np
from bluepy.v2.circuit import Circuit
from bluepy.geometry.roi import ROI
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random import \
    RandomVariate, ConditionedRandomVariate, get_conditioned_random_variate
from dmt.vtk.measurement.condition import ConditionGenerator
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.utils.logging import Logger
from neuro_dmt.models.bluebrain.circuit.parameters \
    import PreMtype, PostMtype, Pathway
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, random_location
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.O1.parameters \
    import RandomRegionOfInterest,  RandomRegionOfInterestByCorticalLayer


cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

#mtype_pre = PreMtype(circuit)
#mtype_post = PostMtype(circuit)

#syn_count = StatisticalMeasurement(method=PairSynapseCount(circuit),
#                                   by=[mtype_pre, mtype_post])



cl = CorticalLayer()


bbcl1 = RandomRegionOfInterestByCorticalLayer(circuit, size=2)
                                             
bbcl2 = RandomRegionOfInterest(circuit,
                               conditioning_variables=(CorticalLayer(),),
                               logger_level=Logger.level.DEVELOP,
                               query=lambda self, condition, target=None:(
                                   {"layer": condition.layer, "$target": target}
                                   if target else
                                   {"layer": condition.layer}))

#bblcrv = get_conditioned_random_variate((cl,), bbcl, circuit=circuit)



class NamedTarget(FiniteValuedParameter):
    """..."""
    value_type = str
    label = "target"
    def __init__(self, *args, **kwargs):
        self.__values = ["mc{}_Column".format(n) for n in range(1, 8)]
        super(NamedTarget, self).__init__(
            value_order = dict(zip(self.__values, range(len(self.__values)))),
            value_repr = dict(zip(self.__values, self.__values)),
            *args, **kwargs
        )
    


nt = NamedTarget()


cg = ConditionGenerator(cl, nt)

