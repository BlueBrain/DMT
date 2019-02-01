"""Test develop random variates for the circuit."""
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
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.parameters\
     import Mtype\
     ,      PreMtype\
     ,      PostMtype\
     ,      MtypePathway
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomCellVariate\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate\
    ,      RandomPosition\
    ,      RandomBoxCorners\
    ,      RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.measurements.connectome\
     import PairConnection\
     ,      PairSynapseCount\
     ,      AfferentConnectionCount\
     ,      EfferentConnectionCount\
     ,      ConnectionStrength\
     ,      SomaDistance

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
        10,
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
        10,
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

random_connection=\
     RandomConnectionVariate(
          circuit_model=sscx_circuit_model
     ).given(
          {pre_mtype, post_mtype})
rcons=\
     random_connection.sample(size=10)
random_pathway_connection=\
     RandomPathwayConnectionVariate(
          circuit_model=sscx_circuit_model
     ).given(
          {pathway})
rpcons=\
     random_pathway_connection.sample(size=10)
sscx_atlas_region=\
     AtlasRegion(
          values=["mc2_Column"])
cortical_layer=\
     CorticalLayer()
random_position=\
     RandomPosition(
          circuit_model=sscx_circuit_model
     ).given(
          {sscx_atlas_region, cortical_layer})
rposes_take=\
     take(
          10,
          random_position)
rposes=\
     random_position.sample(
          size=10)
random_box_corners=\
     RandomBoxCorners(
          circuit_model=sscx_circuit_model
     ).given(
          {sscx_atlas_region, cortical_layer})
rboxes_take=\
     take(
          10,
          random_box_corners)
rboxes=\
     random_box_corners.sample(
          size=10)

logger.info(
     logger.get_source_info(),
     "define some statistical measurements")
conn_measurement=\
     StatisticalMeasurement(
          random_variate=RandomConnectionVariate(
               sscx_circuit_model
          ).given(
               {pre_mtype, post_mtype}))
pre_post_mtype_connections=\
     conn_measurement.get(
          method=PairConnection(
               circuit=sscx_circuit),
          sample_size=10,
          debug=True)
pre_post_mtype_connections_filled=\
     bbadapter.filled(
          pre_post_mtype_connections,
          by={pre_mtype, post_mtype})
pconn_measurement=\
     StatisticalMeasurement(
          random_variate=RandomPathwayConnectionVariate(
               sscx_circuit_model
          ).given(
               {pathway}))
pathway_connections=\
     pconn_measurement.get(
          method=PairConnection(
               circuit=sscx_circuit),
          sample_size=10,
          debug=True)
pathway_connections_filled=\
     bbadapter.filled(
          pathway_connections,
          by={pathway})
cell_group_measurement=\
     StatisticalMeasurement(
          random_variate=RandomCellVariate(
               sscx_circuit_model
          ).given(
               {mtype}))
afferent_counts=\
     cell_group_measurement.get(
          method=AfferentConnectionCount(
               circuit=sscx_circuit),
          sample_size=10,
          debug=True)
afferent_counts_filled=\
     bbadapter.filled(
          afferent_counts,
          by={mtype})
logger.success(
    logger.get_source_info(),
    "All tests passed!")
