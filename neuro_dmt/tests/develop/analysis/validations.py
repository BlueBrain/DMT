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
        inhibitory_synapse_density=InhibitorySynapseDensityValidation,
        synapse_density=SynapseDensityValidation)

    @classmethod
    def get_validation_type(cls,
            phenomenon):
        """..."""
        return cls.ValidationType[phenomenon]

    def get_instance(self,
            phenomenon,
            circuit_regions=None,
            *args, **kwargs):
        """..."""
        circuit_regions=\
            circuit_regions if circuit_regions\
            else self._circuit_regions
        AnalysisType=\
            self.get_analysis_type(
                phenomenon)
        return\
            self.ValidationType[phenomenon](
                phenomenon=phenomenon,
                adapter=self._adapter,
                animal=self._circuit_model.animal,
                measurement_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                spatial_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                plotting_parameter=CorticalLayer(),
                reference_data=ValidationReferenceData.get(phenomenon),
                *args, **kwargs)
               
