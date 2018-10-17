"""Test cell density measurement."""

import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement import StatisticalMeasurement
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper, geometry
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from neuro_dmt.models.bluebrain.circuit.measurements.composition \
    import CellDensity
from neuro_dmt.models.bluebrain.circuit.random_variate \
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.parameters import NamedTarget
from neuro_dmt.models.bluebrain.circuit.O1.parameters import Cortical


cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)
cd = CellDensity(circuit)

rrois\
    = RandomRegionOfInterest(
        circuit,
        circuit_geometry=O1CircuitGeometry,
        brain_region=Cortical(by=("layer", "$target")))\
        .given(CorticalLayer(),
               NamedTarget(
                   values = {"mc2_Column"}))
cds = StatisticalMeasurement(rrois)
data = cds(cd)
