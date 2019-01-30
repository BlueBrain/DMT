"""Test develop cell density validation."""
import os
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.library.bluebrain.circuit.rat.cortex.sscx.composition\
    import validations as rat_validations
from neuro_dmt.library.bluebrain.circuit.mouse.cortex.sscx.composition\
    import validations as mouse_validations
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.library.bluebrain.circuit.models.sscx\
    import get_mouse_sscx_O1_circuit_model,\
    get_rat_sscx_O1_circuit_model,\
    get_sscx_fake_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

get_validations=\
    dict(
        rat=rat_validations,
        mouse=mouse_validations)
project_path=\
    dict(
        rat="/gpfs/bbp.cscs.ch/project/proj64",
        mouse="/gpfs/bbp.cscs.ch/project/proj66")
get_circuit_config_path=\
    dict(
        rat=dict(
            O1=os.path.join(
                project_path["rat"], "circuits",
                "O1.v6a", "20181205", "CircuitConfig"),
            F1=os.path.join(
                project_path["rat"], "circuits",
                "O1.v6a", "20171212", "CircuitConfig"),
            S1=os.path.join(
                project_path["rat"], "circuits",
                "S1.v6a", "20171206", "CircuitConfig")),
        mouse=dict(
            O1=os.path.join(
                project_path["mouse"], "circuits",
                "O1", "20180305", "CircuitConfig"),
            F1=os.path.join(
                project_path["mouse"], "circuits",
                "O1", "20180305", "CircuitConfig")))
get_circuit_model=\
    dict(
        rat=dict(
            O1=get_rat_sscx_O1_circuit_model,
            F1=get_sscx_fake_atlas_circuit_model,
            S1=get_iso_cortex_circuit_model),
        mouse=dict(
            O1=get_mouse_sscx_O1_circuit_model,
            F1=get_sscx_fake_atlas_circuit_model,
            S1=get_iso_cortex_circuit_model))
get_atlas_path=\
    dict(
        rat=dict(
            O1=None,
            F1=os.path.join(
                project_path["rat"], "entities",
                "dev", "atlas",
                "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"),
            S1=os.path.join(
                project_path["rat"], "circuits",
                "S1.v6a", "20171206", ".atlas",
                "C63CB79F-392A-4873-9949-0D347682253A")),
        mouse=dict(
            O1=None,
            F1=os.path.join(
                project_path["mouse"], "entities",
                "dev", "atlas", "O1-152")))
logger=\
    Logger(
        client=__name__,
        level=Logger.level.TEST)

def run(
    animal,
    validation_name,
    circuit_geometry="O1",
    output_dir_path=os.getcwd()):
    """..."""
    logger.info(
        logger.get_source_info(),
        "Will run validation {}".format(validation_name))
    validation=\
        get_validations[animal].get(
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
