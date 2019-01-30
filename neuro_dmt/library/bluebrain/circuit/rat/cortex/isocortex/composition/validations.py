"""Validations of the composition of isocortex circuits for the rat.

Note
---------------------------
As of 20190128 we will use the rat's SSCx composition data to validate
the iso-cortex."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex import\
    MeasureByCorticalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.isocortex.composition\
    import IsoCortexCompositionValidation
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import\
    CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData as ValidationReferenceData

class RatIsocortexCellDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "rat"
        reference_data=\
            ValidationReferenceData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

class RatIsocortexCellRatioValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "rat"
        reference_data=\
            ValidationReferenceData.get(
                "cell_ratio")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

class RatIsocortexSynapseDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "rat"
        reference_data=\
            ValidationReferenceData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

class RatIsocortexInhibitorySynapseDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "rat"
        reference_data=\
            ValidationReferenceData.get(
                "inhibitory_synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


def get(
        validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations=\
        dict(
            cell_density=RatIsocortexCellDensityValidation,
            cell_ratio=RatIsocortexCellRatioValidation,
            inhibitory_synapse_density=RatIsocortexInhibitorySynapseDensityValidation,
            synapse_density=RatIsocortexSynapseDensityValidation)
    try:
        return\
            available_validations[validation_name](
                output_dir_path=output_dir_path)
    except KeyError as e:
        raise NotImplementedError(
            """Validation named {}.\n \tKeyError: {}.\n
            Available validations: \n {}"""\
            .format(
                validation_name, e,
                '\n'.join(
                    "\t{}".format(v) for v in available_validations.keys())) )


