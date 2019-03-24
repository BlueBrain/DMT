"""Test develop neocortex validations.
This file exists to limit repeating commands in an ipython session."""

from neuro_dmt.tests.develop.circuits import *
from neuro_dmt.tests.develop.neocortex import *

all_mtypes=\
    sorted(
        list(sscx_circuit_model_eff.cells.mtypes))
def get_neocortical_analysis_suite_sscx(
        mtypes=all_mtypes,
        *args, **kwargs):
    """..."""
    return\
        NeocortexAnalysisSuite(
            sscx_circuit_model_eff,
            mtype_values=mtypes,
            region_values=["mc2_Column"],
            *args, **kwargs)
def get_neocortical_analysis_suite_isocortex(
        mtypes=all_mtypes,
        region="SSp-ll",
        hemisphere="left",
        direction="eff",
        *args, **kwargs):
    """..."""
    return\
        NeocortexAnalysisSuite(
            IsocortexCircuitModel(
                region=region,
                hemisphere=hemisphere,
                direction=direction),
            mtype_values=mtypes,
            region_values=["region@{}".format(hemisphere)],
            *args, **kwargs)
def run_sscx_synapse_count_analysis(
        mtypes):
    return\
        get_neocortical_analysis_suite_sscx(mtypes)\
          .get_report(
              "pair_synapse_count",
              region="mc2_Column",
              analysis_type="analysis",
              sample_size=200)

def run_sscx_connection_probability_analysis(
        mtypes):
    return\
        get_neocortical_analysis_suite_sscx(mtypes)\
          .get_report(
              "pathway_connection_probability",
              region="mc2_Column",
              analysis_type="analysis",
              sample_size=1000,
              upper_bound_soma_distance=100,
              cache_size=100)
def run_isocortex_connection_probability_analysis(
        mtypes):
    """..."""
    return\
        get_neocortical_analysis_suite_isocortex(mtypes)\
          .get_report(
              "pathway_connection_probability",
              region="SSp-ll@left",
              analysis_type="analysis",
              sample_size=1000,
              upper_bound_soma_distance=100,
              cache_size=100)

# neocortical_analysis_suite_iso_bad=\
#     NeocortexAnalysisSuite(
#         IsocortexCircuitModel(
#             "SSp-ll",
#             use_backup_circuit=True),
#         mtype_values=mtypes)
