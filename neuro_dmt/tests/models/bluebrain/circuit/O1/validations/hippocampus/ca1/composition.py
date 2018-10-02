"""Test develop cell density validation."""
import sys
import os
from bluepy.v2.circuit import Circuit
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.library.bluebrain.circuit.O1.hippocampus.ca1 import composition
from neuro_dmt.utils import brain_regions

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj42/circuits",
                                   "O1", "20180821", "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)
                

def reference_data_path(validation_name):
    """..."""
    return os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                        "work/validations/dmt",
                        "examples/datasets/hippocampus/ca1/mouse",
                        validation_name)

def run(validation_name, plotter=BarPlotComparison):
    """..."""
    logger.info("Will run validation {}".format(validation_name))
    logger.info(
        "Will get validation {}".format(validation_name),
        "Data will load from {}"\
    validation = composition.validation[validation_name]()
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(validation.__class__)
    )
    return validation(reference_data_path(validation_name), circuit_config_path)
                      
