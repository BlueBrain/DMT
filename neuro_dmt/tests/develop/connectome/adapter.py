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
from neuro_dmt.models.bluebrain.circuit.adapter\
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
mtypes=\
    sorted(
        list(
            sscx_circuit_model_nrn.cells.mtypes))
conn_prob=\
    adapter.get_pathway_connection_probability(
        sscx_circuit_model_nrn,
        parameters=[
            AtlasRegion(label="region", values=["mc2_Column"]),
            Mtype(label="pre_mtype", values=mtypes),
            Mtype(label="post_mtype", values=mtypes)],
        cache_size=10)
