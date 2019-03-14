"""A script to run some connectome validations"""
import time
import datetime
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.neocortex\
    import *

logger = Logger(
    "Isocortex validations.",
    level=Logger.level.DEBUG)

def usage():
    logger.info(
        "Explain how to use.")

if __name__=="__main__":
    logger.info(
        logger.get_source_info(),
        logger.info(
            "run validations and analysis"))
    ssp_ll_left_circuit_model=\
        IsocortexCircuitModel(
            region="SSp-ll",
            hemisphere="left",
            direction="eff")
    neocortex_analysis_suite=\
        NeocortexAnalysisSuite(
            ssp_ll_left_circuit_model,
            region_values=["SSp-ll@left"],
            sample_size=200,
            output_dir_path=os.path.join(
                "/gpfs/bbp.cscs.ch/home/sood/work/validations",
                "release/neocortex-2019/arxiv"))
    synapse_count_analysis=\
        neocortex_analysis_suite.get_instance(
            "pair_synapse_count",
            circuit_regions=AtlasRegion(
                values=["SSp-ll@left"]),
            analysis_type="validation")
    synapse_count_measurement=\
        synapse_count_analysis.get_measurement(
            ssp_ll_left_circuit_model,
            is_permissinble = lambda c: synapse_count_analysis.is_permissible(
                c.as_dict))
    synapse_count_measurement.to_csv(
        "syanpse_count.csv")

