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
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            circuit_geometry,
            *args, **kwargs):
        """..."""
        self.animal = "rat"
        reference_data\
            = RatSomatosensoryCortexCompositionData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            circuit_geometry=circuit_geometry,
            *args, **kwargs)


class RatSomatosensoryCortexCellRatioValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellRatioValidation):
    """..."""

    def __init__(self,
            circuit_geometry,
            *args, **kwargs):
        """..."""
        self.animal = "rat"
        reference_data\
            = RatSomatosensoryCortexCompositionData.get(
                "cell_ratio")
        super().__init__(
            reference_data=reference_data,
            circuit_geometry=circuit_geometry,
            *args, **kwargs)
        

class RatSomatosensoryCortexInhibitorySynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        InhibitorySynapseDensityValidation):
    """..."""

    def __init__(self,
            circuit_geometry,
            *args, **kwargs):
        """..."""
        self.animal = "rat"
        reference_data\
            = RatSomatosensoryCortexCompositionData.get(
                "inhibitory_synapse_density")
        super().__init__(
            reference_data=reference_data,
            circuit_geometry=circuit_geometry,
            *args, **kwargs)


class RatSomatosensoryCortexSynapseDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        SynapseDensityValidation):
    """..."""

    def __init__(self,
            circuit_geometry,
            *args, **kwargs):
        """..."""
        self.animal = "rat"
        reference_data\
            = RatSomatosensoryCortexCompositionData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            circuit_geometry=circuit_geometry,
            *args, **kwargs)


def get(validation_name,
        circuit_geometry,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations = dict(
        cell_density=RatSomatosensoryCortexCellDensityValidation,
        cell_ratio=RatSomatosensoryCortexCellRatioValidation,
        inhibitory_synapse_density=RatSomatosensoryCortexInhibitorySynapseDensityValidation,
        synapse_density=RatSomatosensoryCortexSynapseDensityValidation)
    try:
        return available_validations[validation_name](
            circuit_geometry=circuit_geometry,
            output_dir_path=output_dir_path)
    except KeyError as e:
        raise NotImplementedError(
            "Validation named {}.\n \tKeyError: {}.\n Available validations: \n {}"\
            .format(
                validation_name, e,
                '\n'.join(
                    "\t{}".format(v) for v in available_validations.keys())) )
