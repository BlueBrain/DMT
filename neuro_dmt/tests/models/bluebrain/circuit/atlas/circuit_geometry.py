import os
from bluepy.v2.circuit\
    import Circuit
from dmt.vtk.measurement.condition\
    import Condition
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion, CorticalLayer
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import *
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import *
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.library.bluebrain.circuit.models.sscx\
    import get_rat_sscx_O1_circuit_model,\
    get_sscx_fake_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "dev-large/20180904/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_adapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)

iso_geometry=\
    iso_circuit_model.geometry

random_pos=\
    iso_geometry.random_position(
        condition=Condition([
            ("region", "SSp-ll"),
            ("depth", 0.1)]))
ssp_ll_column=\
    iso_geometry.get_cortical_column(
        "SSp-ll")
sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64/circuits",
        "O1.v6a/20171212/",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_fake_atlas_circuit_model(
        sscx_circuit_config,
        "rat")
sscx_adapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
