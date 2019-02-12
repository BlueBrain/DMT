"""Validations of the mouse iso-cortex model"""


import os
from neuro_dmt.library.bluebrain.circuit.mouse.cortex.isocortex.composition\
    import MouseIsocortexCellDensityValidation\
    ,      MouseIsocortexCellRatioValidation\
    ,      MouseIsocortexInhibitorySynapseDensityValidation\
    ,      MouseIsocortexSynapseDensityValidation

def get(
        validation_category,
        validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations={
        "composition": {
            "cell_density": MouseIsocortexCellDensityValidation,
            "cell_ratio": MouseIsocortexCellRatioValidation,
            "inhibitory_synapse_density": MouseIsocortexInhibitorySynapseDensityValidation,
            "synapse_density": MouseIsocortexSynapseDensityValidation} }
        
    try:
        return\
            available_validations[validation_category][validation_name](
                output_dir_path=output_dir_path)
    except KeyError as exception_error:
        raise NotImplementedError(
            """Validation {} {}.\n \tKeyError: {}.\n
            Available validations: \n composition: \n \t {}
            \n connectome: \n \t {}"""\
            .format(
                validation_category,
                validation_name,
                exception_error,
                '\n'.join(
                    "\t{}".format(v)
                    for v in available_validations["composition"].keys())),
            '\n'.join(
                "\t{}".format(v)
                for v in available_validations["connectome"].keys()))
