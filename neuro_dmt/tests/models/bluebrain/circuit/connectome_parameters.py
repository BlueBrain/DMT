"""Test develop connectome parameters"""
import os
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.logging import Logger
from dmt.vtk.utils.collections import take
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
    import Mtype, Pathway

logger=\
    Logger(
        "Test develop random variates",
        level=Logger.level.DEVELOP)
iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "dev-large/20180904/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
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
mtypes=\
    Mtype(
        sscx_circuit,
        values=["L2_IPC", "L2_TPC:A", "L23_TPC", "FOO"])
pathways=\
    Pathway(
        sscx_circuit,
        pre_mtypes=mtypes.values,
        post_mtypes=mtypes.values)

