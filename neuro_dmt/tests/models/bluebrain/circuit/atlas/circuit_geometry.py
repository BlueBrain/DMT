import os
from bluepy.v2.circuit import Circuit
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.atlas.build import *
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest


iso_circuit\
    = Circuit(
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68/circuits",
            "dev-large/20180904/",
            "CircuitConfig"))
bb_adapter\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        circuit_geometry_type=CortexAtlasCircuitGeometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=5)




