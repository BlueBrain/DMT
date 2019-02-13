"""Test develop (generic) neuro_dmt Validations"""
from neuro_dmt.tests.develop.analysis import *
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData as ValidationReferenceData
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation\
    ,      CellRatioValidation\
    ,      InhibitorySynapseDensityValidation\
    ,      SynapseDensityValidation

logger=\
    Logger(
        "Test develop neuro_dmt Validations")

class TestCompositionValidation(
        TestCompositionAnalysis):
    """Test behavior of Composition Validation subclasses"""

    ValidationType=dict(
        cell_density=CellDensityValidation,
        cell_ratio=CellRatioValidation,
        inh_syn_density=InhibitorySynapseDensityValidation,
        syn_density=SynapseDensityValidation)

    def get_instance(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        return self.ValidationType[phenomenon](
            phenomenon=phenomenon,
            adapter = self._adapter,
            animal  = self._circuit_model.animal,
            measurement_parameters = self._measurement_parameters,
            spatial_parameters = self._measurement_parameters,
            plotting_parameter = CorticalLayer(),
            reference_data = ValidationReferenceData.get(phenomenon),
            *args, **kwargs)
               
