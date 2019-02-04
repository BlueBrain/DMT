"""..."""

import os
from neuro_dmt.library.bluebrain.circuit.cortex\
    import MeasureByCorticalLayer
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionValidation
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation\
    ,      CellRatioValidation\
    ,      InhibitorySynapseDensityValidation\
    ,      SynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData


class RatSSCxCellDensityValidation(
        SomatosensoryCortexCompositionValidation,
        MeasureByCorticalLayer,
        CellDensityValidation):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.animal= "rat"
        reference_data=\
            RatSSCxCompositionData.get(
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
            RatSSCxCompositionData.get(
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
            RatSSCxCompositionData.get(
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
            RatSSCxCompositionData.get(
                "synapse_density")
        super().__init__(
            reference_data=reference_data,
            *args, **kwargs)

