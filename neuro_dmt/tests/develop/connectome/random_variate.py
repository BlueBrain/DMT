"""Test develop random variates for connectome analysis."""
import os
import pandas as pd
from dmt.vtk.measurement.condition\
    import Condition\
    ,      ConditionGenerator
from dmt.vtk.measurement.parameter.spatial\
    import DistanceBinner
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomCellVariate\
    ,      RandomPairs\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome.\
    pair_synapse_count import RatSSCxPairSynapseCountData
from neuro_dmt.tests.develop.circuits\
    import *
from neuro_dmt.measurement.parameter\
    import *
from neuro_dmt.measurement.parameter.spatial\
    import *
from neuro_dmt.models.bluebrain.circuit.parameters\
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
        sscx_circuit_model_nrn)
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
all_mtypes=\
    sorted(list(
        sscx_circuit_model_nrn.cells.mtypes))
# soma_distance=\
#     SomaDistance(0, 500, 1)
# random_pairs_sscx_nrn_AB=\
#     RandomPairs(
#         sscx_circuit_model_nrn,
#         distance_binner=soma_distance._binner)
# mtypes_AB=\
#     ["L5_TPC:A", "L5_TPC:B"]
# parameters_AB=[
#     AtlasRegion(values=["mc2_Column"]),
#     Mtype(label="pre_mtype", values=mtypes_AB),
#     Mtype(label="post_mtype", values=mtypes_AB),
#     soma_distance]
# rps_AB = pd.concat([
#     random_pairs_sscx_nrn_AB.sample_one(condition, size=1000)
#     for condition in ConditionGenerator(*parameters_AB)])
# conditions_AB=\
#     pd.concat([
#         pd.DataFrame([
#             condition.as_dict
#             for condition in ConditionGenerator(*parameters_AB)])])
# random_pairs_sscx_nrn_BA=\
#     RandomPairs(
#         sscx_circuit_model_nrn,
#         distance_binner=soma_distance._binner)
# mtypes_BA=\
#     ["L5_TPC:B", "L5_TPC:A"]
# parameters_BA=[
#     AtlasRegion(values=["mc2_Column"]),
#     Mtype(label="pre_mtype", values=mtypes_BA),
#     Mtype(label="post_mtype", values=mtypes_BA),
#     soma_distance]
# rps_BA = pd.concat([
#     random_pairs_sscx_nrn_BA.sample_one(condition, size=1000)
#     for condition in ConditionGenerator(*parameters_BA)])
# conditions_BA=\
#     pd.concat([
#         pd.DataFrame([
#             condition.as_dict
#             for condition in ConditionGenerator(*parameters_BA)])])

# random_pairs_sscx_nrn_BB=\
#     RandomPairs(
#         sscx_circuit_model_nrn,
#         distance_binner=soma_distance._binner)
# mtypes_BB=\
#     ["L5_TPC:B"]
# parameters_BB=[
#     AtlasRegion(values=["mc2_Column"]),
#     Mtype(label="pre_mtype", values=mtypes_BB),
#     Mtype(label="post_mtype", values=mtypes_BB),
#     soma_distance]
# rps_BB = pd.concat([
#     random_pairs_sscx_nrn_BB.sample_one(condition, size=1000)
#     for condition in ConditionGenerator(*parameters_BB)])
# conditions_BB=\
#     pd.concat([
#         pd.DataFrame([
#             condition.as_dict
#             for condition in ConditionGenerator(*parameters_BB)])])

soma_distance=\
    SomaDistance(
        0., 500., 2)
parameters=[
    AtlasRegion(values=["mc2_Column"]),
    Mtype(label="pre_mtype", values=all_mtypes),
    Mtype(label="post_mtype", values=all_mtypes),
    soma_distance]
random_pairs=\
    RandomPairs(
        sscx_circuit_model_nrn,
        distance_binner=soma_distance._binner)
