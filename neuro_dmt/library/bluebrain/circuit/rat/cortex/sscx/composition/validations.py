"""..."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex import\
    MeasureByCorticalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.composition import \
    SomatosensoryCortexCompositionValidation
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSSCxCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal=\
            "rat"
        reference_data=\
            RatSomatosensoryCortexCompositionData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


class RatSSCxCellRatioValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellRatioValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal=\
            "rat"
        reference_data=\
            RatSomatosensoryCortexCompositionData.get(
                "cell_ratio")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)
        

class RatSSCxInhibitorySynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        InhibitorySynapseDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal=\
            "rat"
        reference_data=\
            RatSomatosensoryCortexCompositionData.get(
                "inhibitory_synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


class RatSSCxSynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        SynapseDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal=\
            "rat"
        reference_data=\
            RatSomatosensoryCortexCompositionData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


def get(validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations= dict(
        cell_density=RatSSCxCellDensityValidation,
        cell_ratio=RatSSCxCellRatioValidation,
        inhibitory_synapse_density=RatSSCxInhibitorySynapseDensityValidation,
        synapse_density=RatSSCxSynapseDensityValidation)
    try:
        return available_validations[validation_name](
            output_dir_path=output_dir_path)
    except KeyError as e:
        raise NotImplementedError(
            """Validation named {}.\n \tKeyError: {}.\n
            Available validations: \n {}"""\
            .format(
                validation_name, e,
                '\n'.join(
                    "\t{}".format(v) for v in available_validations.keys())) )
