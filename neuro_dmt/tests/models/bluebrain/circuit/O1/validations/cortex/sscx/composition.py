"""Test develop cell density validation."""
import os
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.logging import Logger
from neuro_dmt.library.bluebrain.circuit.rat.cortex.sscx.composition\
    import validations
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit

circuit_config_path\
    = os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64/circuits",
        "O1.v6a", "20171212", "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)
                
def run(validation_name, output_dir_path=os.getcwd()):
    """..."""
    logger.info(
        "Will run validation {}".format(validation_name))
    validation\
        = validations.get(
            validation_name,
            circuit_build=O1Circuit,
            output_dir_path=output_dir_path)
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(validation.__class__))
    report\
        = validation(
            Circuit(circuit_config_path),
            save_report=True)
    return report
                      
