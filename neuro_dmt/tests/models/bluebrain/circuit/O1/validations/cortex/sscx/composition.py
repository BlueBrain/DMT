"""Test develop cell density validation."""
import os
from bluepy.v2.circuit import Circuit
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.logging import Logger
from neuro_dmt.library.bluebrain.circuit.cortex.sscx import composition
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj64/circuits",
                                   "O1.v6a", "20171212", "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)
                
def run(validation_name):
    """..."""
    logger.info("Will run validation {}".format(validation_name))
    v = composition.validation(validation_name, circuit_build=O1Circuit)
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(v.__class__)
    )
    r = v(Circuit(circuit_config_path))
    r.save()
    return r
                      
