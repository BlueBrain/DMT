"""Test develop specialized connectome methods for the Adapter"""


"""Test develop random variates for connectome analysis."""
import os
import pandas as pd
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.measurement.parameter.spatial\
    import DistanceBinner
from neuro_dmt.measurement.parameter\
    import AtlasRegion
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomCellVariate\
    ,      RandomPairs\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate
from neuro_dmt.models.bluebrain.circuit.adapter.connetome_adapter\
    import *
from neuro_dmt.tests.develop.circuits\
    import *

adapter=\
    BlueBrainModelAdapter(
        brain_region=sscx_circuit_model_nrn.brain_region,
        sample_size=20,
        sampled_box_shape=50.*np.ones(3),
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")
connectome_adapter=\
    BlueBrainModelConnectomeAdapter(
        brain_region=sscx_circuit_model_nrn.brain_region,
        sample_size=20,
        sampled_box_shape=50.*np.ones(3),
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")
all_mtypes=\
    sorted(
        list(
            sscx_circuit_model_nrn.cells.mtypes))
def get_connection_probabilities(
        circuit_model,
        region,
        mtypes,
        upper_bound_soma_distance=300,
        using_connectome_adapter=True,
        cache_size=100,
        sample_size=200):
    """..."""
    if using_connectome_adapter:
        return\
            connectome_adapter\
              .get_pathway_connection_probability(
                  circuit_model,
                  parameters=[
                      AtlasRegion(label="region", values=[region]),
                      Mtype(label="pre_mtype", values=mtypes),
                      Mtype(label="post_mtype", values=mtypes)],
                  upper_bound_soma_distance=upper_bound_soma_distance,
                  cache_size=cache_size,
                  sample_size=sample_size)
    return\
        adapter\
          .get_pathway_connection_probability(
              circuit_model,
              parameters=[
                  AtlasRegion(label="region", values=[region]),
                  Mtype(label="pre_mtype", values=mtypes),
                  Mtype(label="post_mtype", values=mtypes)],
              sample_size=sample_size,
              is_permissible=lambda condition: True)
