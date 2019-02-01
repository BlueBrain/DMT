"""Test develop connectome analysis."""

import os
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.logging import Logger
from dmt.vtk.utils.collections import take
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion\
    ,      CorticalLayer\
    ,      CorticalDepth
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_fake_atlas_circuit_model
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.parameters\
     import Mtype\
     ,      PreMtype\
     ,      PostMtype\
     ,      MtypePathway

logger=\
    Logger(
        "Test develop random variates",
        level=Logger.level.DEVELOP)
bbadapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "dev-large/20180904/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_circuit=\
     iso_circuit_model.bluepy_circuit
sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "O1.v6a/20171212",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_fake_atlas_circuit_model(
        sscx_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64", "entities",
            "dev", "atlas",
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"))
sscx_circuit=\
    sscx_circuit_model.bluepy_circuit
mtype=\
    Mtype(
         sscx_circuit,
         values=["L4_TPC", "L2_TPC:A", "L3_TPC:A", "FOO"])
pre_mtype=\
    PreMtype(
        sscx_circuit,
         values=mtype.values)
post_mtype=\
    PostMtype(
         sscx_circuit,
         values=mtype.values)
pathway=\
    MtypePathway(
        sscx_circuit,
        pre_mtypes=mtype.values,
        post_mtypes=mtype.values)

syn_count=\
    bbadapter.get_pathway_synapse_count(
        sscx_circuit_model,
        parameters=[pre_mtype, post_mtype],
        sample_size=5,
        debug=True)
cnxn_strength=\
    bbadapter.get_pathway_connection_strength(
        sscx_circuit_model,
        parameters=[pre_mtype, post_mtype],
        sample_size=5,
        debug=True)
cnxn_count=\
    bbadapter.get_pathway_connection_count(
        sscx_circuit_model,
        parameters=[pre_mtype, post_mtype],
        sample_size=5,
        debug=True)
soma_distance=\
    bbadapter.get_pathway_soma_distance(
        sscx_circuit_model,
        parameters=[pre_mtype, post_mtype],
        sample_size=5,
        debug=True)

logger.success(
    logger.get_source_info(),
    "All tests passed!")
