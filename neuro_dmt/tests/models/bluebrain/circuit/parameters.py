"""Test develop Blue Brain circuit parameters."""

from bluepy.v2.circuit import Circuit
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameters import get_grouped_values
from neuro_dmt.models.bluebrain.circuit.parameters \
    import PreMtype, PostMtype, Pathway
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

mtype_pre = PreMtype(circuit)
mtype_post = PostMtype(circuit)

syn_count = StatisticalMeasurement(method=PairSynapseCount(circuit),
                                   by=[mtype_pre, mtype_post])




