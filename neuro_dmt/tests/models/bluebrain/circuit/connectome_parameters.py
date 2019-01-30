"""Test develop connectome parameters"""
import os
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.collections\
    import take
from dmt.vtk.measurement\
    import StatisticalMeasurement
from dmt.vtk.measurement.condition\
    import Condition
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion, CorticalLayer, CorticalDepth
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.sscx\
    import get_sscx_fake_atlas_circuit_model
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype\
    ,      PreMtype\
    ,      PostMtype\
    ,      MtypePathway
from neuro_dmt.models.bluebrain.circuit.measurements.connectome\
    import *
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest\
    ,      RandomCellVariate\
    ,      RandomConnectionVariate


logger=\
    Logger(
        "Test develop random variates",
        level=Logger.level.DEVELOP)
# iso_circuit_config=\
#     os.path.join(
#         "/gpfs/bbp.cscs.ch/project/proj68/circuits",
#         "dev-large/20180904/",
#         "CircuitConfig")
# iso_circuit_model=\
#     get_iso_cortex_circuit_model(
#         iso_circuit_config,
#         "mouse")
sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64/circuits/",
        "O1.v6a/20181207",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_fake_atlas_circuit_model(
        sscx_circuit_config,
        "rat")
sscx_circuit=\
    sscx_circuit_model.circuit
mtype=\
    Mtype(
        sscx_circuit,
        values=["L2_IPC", "L2_TPC:A", "L23_TPC", "FOO"])
pre_mtype=\
    PreMtype(
        sscx_circuit,
        values=["L2_IPC", "L2_TPC:A", "L23_TPC", "FOO"])
post_mtype=\
    PostMtype(
        sscx_circuit,
        values=["L2_IPC", "L2_TPC:A", "L23_TPC", "FOO"])
pathway=\
    MtypePathway(
        sscx_circuit,
        pre_mtypes=mtype.values,
        post_mtypes=mtype.values)
bbadapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
cell_gid_measurement=\
    StatisticalMeasurement(
        random_variate=RandomCellVariate(
            sscx_circuit_model
        ).given({
            mtype}))
cnxn_measurement=\
    StatisticalMeasurement(
        random_variate=RandomConnectionVariate(
            sscx_circuit_model
        ).given({
            pre_mtype,
            post_mtype}))
