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
from neuro_dmt.tests.develop.circuits\
    import *

isocortex_model=\
    IsocortexCircuitModel(
        region="SSp-ll",
        hemisphere="left",
        direction="eff")
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
random_connections_isocortex=\
    RandomConnectionVariate(
        isocortex_model,
        cache_size=100)
random_connections_sscx_son=\
    RandomConnectionVariate(
        sscx_circuit_model_eff,
        cache_size=100)
random_connections_sscx_nrn=\
    RandomConnectionVariate(
        sscx_circuit_model_nrn,
        cache_size=100)
# l5_tpca_tpca=\
#     random_connections.sample_one(
#         Condition([
#             ("pre_mtype", "L5_TPC:A"),
#             ("post_mtype", "L5_TPC:A"),
#             ("region", "SSp-ll@left")]))
