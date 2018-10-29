"""Test develop cell density validation."""
import os
from bluepy.v2.circuit\
    import Circuit
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
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest

validations\
    = dict(
        rat=rat_validations,
        mouse=mouse_validations)
circuit_config_path\
    = dict(
        rat=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
            "O1.v6a", "20171212", "CircuitConfig"),
        mouse=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj66/circuits",
            "O1", "20180305", "CircuitConfig") )


logger = Logger(client=__name__, level=Logger.level.TEST)
                
def run(animal, validation_name, output_dir_path=os.getcwd()):
    """..."""
    logger.info(
        "Will run validation {}".format(validation_name))

    animal_validations = validations[animal]
    animal_circuit_config_path = circuit_config_path[animal]

    validation\
        = animal_validations.get(
            validation_name,
            circuit_geometry_type=O1CircuitGeometry,
            output_dir_path=output_dir_path)
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(validation.__class__))
    report\
        = validation(
            Circuit(animal_circuit_config_path),
            save_report=True)
    return report

rat_circuit\
    = Circuit(circuit_config_path["rat"])
mouse_circuit\
    = Circuit(circuit_config_path["mouse"])
bbma\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        circuit_geometry_type=O1CircuitGeometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")
