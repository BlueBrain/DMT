"Some adhoc tests"

import pandas as pd
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.circuits\
    import *

logger = Logger(
    "Adhoc tests for the isocortex connetome",
    level=Logger.level.DEBUG)
def get_number_connections(
        connectome,
        pre_mtype,
        post_mtype,
        region):
    """..."""
    connections=\
        connectome.iter_connections(
            {"mtype": pre_mtype, "region": region},
            {"mtype": post_mtype, "region": region})
    number=\
        sum(1 for _ in connections)
    logger.info(
        "pre_mtype {}, post_mtype {}, connections {}"\
        .format(pre_mtype, post_mtype, number))
    return number

sscx_nrn_connectome=\
    sscx_circuit_model_nrn.connectome
mtypes=\
    sscx_circuit_model_nrn.cells.mtypes
sscx_sonata_connectome=\
    sscx_circuit_model_eff.connectome
iso_connectome=\
    IsocortexCircuitModel(
        region="SSp-ll",
        hemisphere="left",
        direction="aff"
    ).connectome

def run(
        connectome,
        mtype_pairs,
        region,
        file_name):
    connections=\
        pd.DataFrame([
            {"pre_mtype": pre_mtype,
             "post_mtype": post_mtype,
             "number_connections": get_number_connections(
                 connectome,
                 pre_mtype,
                 post_mtype,
                 region)}
            for pre_mtype, post_mtype in mtype_pairs])
    connections.to_csv(
        os.path.join(
            "/gpfs/bbp.cscs.ch/home/sood/",
            "work/validations/",
            "release", "neocortex-2019", "arxiv",
            "validation", "mouse", "somatosensory_cortex",
            "connectome", "adhoc",
            file_name))

