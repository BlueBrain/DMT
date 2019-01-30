"""Test develop random variates for the circuit."""
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
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomCellVariate

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
    sscx_circuit_model.bluepy_circuit
random_sscx_cell_gids=\
    take(
        100,
        RandomCellVariate(
            circuit_model=sscx_circuit_model,
            conditions={
                Condition([("mtype", "L2_IPC")])}))

for cell_gid in random_sscx_cell_gids:
     cell_mtypes=\
         sscx_circuit.cells\
                     .get(
                         cell_gid, properties=["mtype"])\
                     .values
     assert len(cell_mtypes) == 1
     assert cell_mtypes[0] == "L2_IPC"

random_iso_cell_gids=\
    take(
        100,
        RandomCellVariate(
            circuit_model=iso_circuit_model,
            conditions={
                Condition([("mtype", "L2_IPC")])}))

for cell_gid in random_iso_cell_gids:
     cell_mtypes=\
         iso_circuit.cells\
                     .get(
                         cell_gid, properties=["mtype"])\
                     .values
     assert len(cell_mtypes) == 1
     assert cell_mtypes[0] == "L2_IPC"

logger.success(
    logger.get_source_info(),
    "All tests passed!")
