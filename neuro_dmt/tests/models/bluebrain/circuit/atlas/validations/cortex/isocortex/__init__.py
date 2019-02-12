"""Test develop validations for the iso-cortex"""
import os
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.library.bluebrain.circuit.mouse.cortex.isocortex\
    import validations as mouse_validations
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

get_validations=\
    dict(
        mouse=mouse_validations)
project_path=\
    dict(
        mouse="/gpfs/bbp.cscs.ch/project/proj68/")
get_circuit_config_path=\
    dict(
        mouse=dict(
            S1=os.path.join(
                project_path["mouse"], "circuits",
                "Isocortex", "20190212", "CircuitConfig")))
get_circuit_model=\
    dict(
        mouse=dict(
            S1=get_iso_cortex_circuit_model))
get_atlas_path=\
    dict(
        mouse=dict(
            S1=None))
logger=\
    Logger(
        client=__name__,
        level=Logger.level.TEST)

def run(
    animal,
    validation_category,
    validation_name,
    region="SSp-ll",
    circuit_geometry="S1",
    output_dir_path=os.getcwd()):
    """..."""
    logger.info(
        logger.get_source_info(),
        "Will run validation {}".format(validation_name))
    validation=\
        get_validations[animal].get(
            validation_category,
            validation_name,
            output_dir_path=output_dir_path)
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(
            validation.__class__))
    circuit_model=\
        get_circuit_model[animal][circuit_geometry](
            circuit_config=get_circuit_config_path[animal][circuit_geometry],
            animal=animal,
            atlas_path=get_atlas_path[animal][circuit_geometry])
    report=\
        validation(
            circuit_model,
            save_report=True)
    return report

#run("rat", "cell_density")
#run("mouse", "cell_ratio")
