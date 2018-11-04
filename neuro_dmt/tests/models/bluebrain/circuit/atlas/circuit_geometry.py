import os
from bluepy.v2.circuit import Circuit
from neuro_dmt.measurement.parameter\
    import AtlasRegion, CorticalLayer
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.atlas.build import *
from neuro_dmt.models.bluebrain.circuit.O1.build import *
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest


iso_circuit\
    = Circuit(
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68/circuits",
            "dev-large/20180904/",
            "CircuitConfig"))
iso_adapter\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        circuit_geometry_type=CortexAtlasCircuitGeometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=100)

sscx_circuit\
    = Circuit(
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
            "O1.v6a/20171212/",
            "CircuitConfig"))

sscx_adapter\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        circuit_geometry_type=SSCxO1CircuitGeometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=100)





