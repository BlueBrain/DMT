"""Test develop cell density validation."""
import sys
import os
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.library.bluebrain.circuit.O1.hippocampus.ca1 import composition

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj42/circuits",
                                   "O1", "20180821", "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)
                

def reference_data_path(validation_name):
    """..."""
    return  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                         "work/validations/dmt",
                         "examples/datasets/cortex/sscx/rat",
                         validation_name)

def get_validation(validation_name):
    """..."""
    logger.info("Will get validation {}".format(validation_name))
    logger.info("Data will load from {}"\
                .format(reference_data_path(validation_name)))

    return composition.validation[validation_name](
        brain_regions.cortex,
        with_plotter=BarPlotComparison
    ).get_validation(reference_data_path(validation_name))

def run(validation_name):
    """..."""
    logger.info("Will run validation {}".format(validation_name))
    logger.info("Data will load from {}"\
                .format(reference_data_path(validation_name)))

    validation = composition.validation[validation_name](
        brain_regions.cortex,
        with_plotter=BarPlotComparison
    )
    return validation(reference_data_path(validation_name),
                      circuit_config_path)
def run(validation_name):
    """..."""
    print("Will run validation {}".format(validation_name))
    reference_data_path =  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                        "work/validations/dmt",
                                        "examples/datasets/hippocampus/ca1/mouse",
                                        validation_name)
    print("Data will load from {}".format(reference_data_path))
    cdv = composition.validation[validation_name]()
    print("Loaded {}".format(cdv))
    cdv(reference_data_path, circuit_config_path)
