"""..."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex import\
    MeasureByCorticalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.composition import \
    SomatosensoryCortexCompositionValidation
from neuro_dmt.validations.circuit.composition.by_layer import\
    CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSomatosensoryCortexCompositionData

class MouseSomatosensoryCortexCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            circuit_build,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            circuit_build=circuit_build,
            *args, **kwargs)


class MouseSomatosensoryCortexCellRatioValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellRatioValidation):
    """..."""
    def __init__(self,
            circuit_build,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "cell_ratio")
        super().__init__(
            reference_data=reference_data,
            circuit_build=circuit_build,
            *args, **kwargs)
        

class MouseSomatosensoryCortexInhibitorySynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        InhibitorySynapseDensityValidation):
    """..."""

    def __init__(self,
            circuit_build,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "inhibitory_synapse_density")
        super().__init__(
            reference_data=reference_data,
            circuit_build=circuit_build,
            *args, **kwargs)


class MouseSomatosensoryCortexSynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        SynapseDensityValidation):
    """..."""

    def __init__(self,
            circuit_build,
            *args, **kwargs):
        """..."""
        self.animal = "mouse"
        reference_data\
            = MouseSomatosensoryCortexCompositionData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            circuit_build=circuit_build,
            *args, **kwargs)


def get(validation_name,
        circuit_build,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations = dict(
        cell_density=MouseSomatosensoryCortexCellDensityValidation,
        cell_ratio=MouseSomatosensoryCortexCellRatioValidation,
        inhibitory_synapse_density=MouseSomatosensoryCortexInhibitorySynapseDensityValidation,
        synapse_density=MouseSomatosensoryCortexSynapseDensityValidation)
    try:
        return available_validations[validation_name](
            circuit_build=circuit_build,
            output_dir_path=output_dir_path)
    except KeyError as e:
        raise NotImplementedError(
            "Validation named {}.\n \tKeyError: {}.\n Available validations: \n {}"\
            .format(
                validation_name, e,
                '\n'.join(
                    "\t{}".format(v) for v in available_validations.keys())) )
