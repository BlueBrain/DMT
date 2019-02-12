"""Validations of the composition of isocortex circuits for the mouse.

Note
---------------------------
As of 20190128 we will use the mouse's SSCx composition data to validate
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
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData as ValidationReferenceData

class MouseIsocortexCellDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "mouse"
        reference_data=\
            ValidationReferenceData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


class MouseIsocortexCellRatioValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "mouse"
        reference_data=\
            ValidationReferenceData.get(
                "cell_mouseio")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

class MouseIsocortexSynapseDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "mouse"
        reference_data=\
            ValidationReferenceData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

class MouseIsocortexInhibitorySynapseDensityValidation(
        IsoCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        self.animal= "mouse"
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
            cell_density=MouseIsocortexCellDensityValidation,
            cell_mouseio=MouseIsocortexCellMouseioValidation,
            inhibitory_synapse_density=MouseIsocortexInhibitorySynapseDensityValidation,
            synapse_density=MouseIsocortexSynapseDensityValidation)
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


