"""SSCx circuit phenomena validations for the mouse."""

import os
from neuro_dmt.library.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCellDensityValidation\
    ,      MouseSSCxCellRatioValidation\
    ,      MouseSSCxInhibitorySynapseDensityValidation\
    ,      MouseSSCxSynapseDensityValidation

def get(
        validation_category,
        validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations={
        "composition": {
            "cell_density": MouseSSCxCellDensityValidation,
            "cell_ratio": MouseSSCxCellRatioValidation,
            "inhibitory_synapse_density": MouseSSCxInhibitorySynapseDensityValidation,
            "synapse_density": MouseSSCxSynapseDensityValidation} }
        
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
