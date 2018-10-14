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
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.parameters \
    import PreMtype, PostMtype, Pathway
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, random_location
from neuro_dmt.models.bluebrain.circuit.O1.parameters import \
    HyperColumn
from neuro_dmt.models.bluebrain.circuit.random_variate import \
    RandomPosition,\
    RandomRegionOfInterest,\
    RandomBoxCorners
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit
from neuro_dmt.models.bluebrain.circuit.measurements.composition\
    import CellDensity


sscx_cpath\
    = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
sscx_circuit\
    = Circuit(sscx_cpath)
hipp_cpath\
    = "/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180219/CircuitConfig"
hipp_circuit\
    = Circuit(hipp_cpath)

logger\
    = Logger(
        client=None,
        name="Parameters",
        level=Logger.level.STUDY)

cortical_layer\
    = CorticalLayer()
hyper_column\
    = HyperColumn()
cond_gen\
    = ConditionGenerator(
        cortical_layer,
        hyper_column)
rposes\
    = RandomPosition(
        sscx_circuit,
        circuit_build=O1Circuit,
        brain_region=brain_regions.cortex)\
        .given(
            CorticalLayer(),
            HyperColumn())

rroies\
    = RandomRegionOfInterest(
        sscx_circuit,
        circuit_build=O1Circuit,
        brain_region=brain_regions.cortex)\
        .given(
            CorticalLayer(),
            HyperColumn(values=[2]))
rboxes\
    = RandomBoxCorners(
        sscx_circuit,
        circuit_build=O1Circuit,
        brain_region=brain_regions.cortex)\
        .given(
            CorticalLayer(),
            HyperColumn(values=[2]))

#testing HyperColumn

hc_roies\
    = RandomRegionOfInterest(
        sscx_circuit,
        circuit_build=O1Circuit,
        brain_region=brain_regions.cortex)\
        .given(
            {HyperColumn()})
get_measurement\
    = StatisticalMeasurement(
        random_variate=hc_roies,
        sample_size=20)
#cell_density\
#    = get_measurement(
 #       CellDensity(sscx_circuit))
