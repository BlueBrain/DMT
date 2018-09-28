"""Test develop cell density validation."""
import os
from bluepy.v2.circuit import Circuit
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.logging import Logger
from neuro_dmt.library.bluebrain.circuit.O1.cortex.sscx import composition
from neuro_dmt.utils import brain_regions

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj64/circuits",
                                   "O1.v6a", "20171212", "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)
                

def reference_data_path(validation_name):
    """..."""
    return  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                         "work/validations/dmt",
                         "examples/datasets/cortex/sscx/rat",
                         validation_name)

def get_validation(validation_name, plotter=BarPlotComparison):
    """..."""
    logger.info(
        "Will get validation {}".format(validation_name),
        "Data will load from {}"\
        .format(reference_data_path(validation_name))
    )
    return composition.validation[validation_name](
        plotter_type=plotter
    )#.get_validation(reference_data_path(validation_name))

def run(validation_name, plotter=BarPlotComparison):
    """..."""
    logger.info("Will run validation {}".format(validation_name))
    validation = get_validation(validation_name, plotter=plotter)
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(validation.__class__)
    )
    return validation(reference_data_path(validation_name),
                      circuit_config_path)
