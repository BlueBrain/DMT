"""Ready to use validations."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex import\
    MeasureByHippocampalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.composition import \
    SomatosensoryCortexCompositionValidation
from neuro_dmt.validations.circuit.composition.by_layer import\
    CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByHippocampalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            circuit_geometry,
            *args, **kwargs):
        """..."""
        reference_data=\
            RatSomatosensoryCortexCompositionData.get(
                "cell_density")
        super().__init__(
            reference_data=reference_data,
            circuit_geometry=circuit_geometry,
            *args, **kwargs)

