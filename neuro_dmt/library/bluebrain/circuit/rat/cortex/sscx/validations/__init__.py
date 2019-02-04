"""SSCx circuit phenomena validations for the rat."""

import os
from neuro_dmt.library.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCellDensityValidation\
    ,      RatSSCxCellRatioValidation\
    ,      RatSSCxInhibitorySynapseDensityValidation\
    ,      RatSSCxSynapseDensityValidation
from neuro_dmt.library.bluebrain.circuit.rat.cortex.sscx.connectome\
    import RatSSCxPairSynapseCountValidation

def get(
        validation_category,
        validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations={
        "composition": {
            "cell_density": RatSSCxCellDensityValidation,
            "cell_ratio": RatSSCxCellRatioValidation,
            "inhibitory_synapse_density": RatSSCxInhibitorySynapseDensityValidation,
            "synapse_density": RatSSCxSynapseDensityValidation},
        "connectome": {
            "pair_synapse_count": RatSSCxPairSynapseCountValidation} }
        
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
