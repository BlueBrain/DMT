"""Test, (and develop), Blue Brain O1 circuit model adapter. """

import numpy as np
from bluepy.v2.circuit import Circuit
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate import \
    RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.O1.geometry import O1CircuitGeometry
    

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

bbma\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        circuit_geometry=O1Circuit.Geometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")

#cd = bbma.get_cell_density(circuit, {CorticalLayer()})



