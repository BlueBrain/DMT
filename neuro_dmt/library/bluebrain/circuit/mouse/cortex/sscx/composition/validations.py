"""..."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex import\
    MeasureByCorticalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.composition import \
    SomatosensoryCortexCompositionValidation
from neuro_dmt.analysis.validation.circuit.composition.by_layer import\
    CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSomatosensoryCortexCompositionData

class MouseSSCxCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


class MouseSSCxCellRatioValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellRatioValidation):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "cell_ratio")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)
        

class MouseSSCxInhibitorySynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        InhibitorySynapseDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "inhibitory_synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


class MouseSSCxSynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        SynapseDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)


def get(validation_name,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations = dict(
        cell_density=MouseSSCxCellDensityValidation,
        cell_ratio=MouseSSCxCellRatioValidation,
        inhibitory_synapse_density=MouseSSCxInhibitorySynapseDensityValidation,
        synapse_density=MouseSSCxSynapseDensityValidation)
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
