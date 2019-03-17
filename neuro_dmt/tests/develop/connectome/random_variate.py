"""Test develop random variates for connectome analysis."""
import os
import pandas as pd
from dmt.vtk.measurement.condition\
    import Condition
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
random_pairs_sscx_nrn=\
    RandomPairs(
        sscx_circuit_model_nrn,
        distance_binner=DistanceBinner(
            0., 1000., 5))

