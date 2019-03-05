"""Test develop random variates for connectome analysis."""
import os
import pandas as pd
from dmt.vtk.measurement.condition\
    import Condition
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomCellVariate\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome.\
    pair_synapse_count import RatSSCxPairSynapseCountData
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_fake_atlas_circuit_model\
   ,      get_sscx_atlas_circuit_model

sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "O1.v6a/20171212",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        sscx_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64", "entities",
            "dev", "atlas",
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"))
sscx_circuit_model.geometry.circuit_specialization.representative_region=\
    "mc2_Column"
sscx_circuit=\
    sscx_circuit_model.bluepy_circuit
sscx_mtypes=\
    sscx_circuit.cells.mtypes
synapse_count_data=\
    RatSSCxPairSynapseCountData().datasets["michael_reimann_2017"].data.data
pathways=\
    [(pre_mtype, post_mtype)
     for pre_mtype, post_mtype in synapse_count_data.index
     if pre_mtype in sscx_mtypes and post_mtype in sscx_mtypes]

def get_pathway_condition(i):
    pre_mtype, post_mtype=\
        pathways[i]
    return\
        Condition([
            ("pre_mtype", pre_mtype),
            ("post_mtype", post_mtype)])

random_cells=\
    RandomCellVariate(
        sscx_circuit_model)
random_connections=\
    RandomConnectionVariate(
        sscx_circuit_model)
