"""Test develop cell density validation."""
import os
from voxcell.nexus.voxelbrain import LocalAtlas
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.library.bluebrain.circuit.rat.cortex.sscx.composition\
    import validations\
    as rat_validations
from neuro_dmt.library.bluebrain.circuit.mouse.cortex.sscx.composition\
    import validations\
    as mouse_validations
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import CircuitModel
from neuro_dmt.library.bluebrain.circuit.models.sscx import\
    get_mouse_sscx_O1_circuit_model,\
    get_rat_sscx_O1_circuit_model,\
    get_sscx_fake_atlas_circuit_model
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest

get_validations=\
    dict(
        rat=rat_validations,
        mouse=mouse_validations)
get_circuit_config_path=\
    dict(
        rat=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
            "O1.v6a", "20171212", "CircuitConfig"),
        mouse=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj66/circuits",
            "O1", "20180305", "CircuitConfig") )
get_circuit_model=\
    dict(
        rat=dict(
            O1=get_rat_sscx_O1_circuit_model,
            S1=get_sscx_fake_atlas_circuit_model),
        mouse=dict(
            O1=get_mouse_sscx_O1_circuit_model,
            S1=get_sscx_fake_atlas_circuit_model))
get_atlas_path=\
    dict(
        rat=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
            "O1.v6a", "20171212", ".atlas", 
            "77831ACA-6198-4AA0-82EF-D0475A4E0647"),
        mouse=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj66/entities",
            "dev", "atlas", "O1-152"))

logger = Logger(client=__name__, level=Logger.level.TEST)

def run(
    animal,
    validation_name,
    circuit_geometry_type="O1",
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
        get_circuit_model[animal][circuit_geometry_type](
            circuit_config=get_circuit_config_path[animal],
            animal=animal,
            atlas_path=get_atlas_path[animal])
    report\
        = validation(
            circuit_model,
            save_report=True)
    return report

#run("rat", "cell_density")
#run("mouse", "cell_ratio")
