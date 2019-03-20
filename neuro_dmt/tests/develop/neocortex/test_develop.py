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
    return\
        NeocortexAnalysisSuite(
            sscx_circuit_model_eff,
            mtype_values=mtypes,
            region_values=["mc2_Column"],
            *args, **kwargs)
def run_synapse_count_analysis(
        mtypes):
    return\
        get_neocortical_analysis_suite_sscx(mtypes)\
        .get_report(
            "pair_synapse_count",
            region="mc2_Column",
            analysis_type="analysis",
            sample_size=200)

# neocortical_analysis_suite_iso_bad=\
#     NeocortexAnalysisSuite(
#         IsocortexCircuitModel(
#             "SSp-ll",
#             use_backup_circuit=True),
#         mtype_values=mtypes)
