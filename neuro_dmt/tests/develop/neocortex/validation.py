"""Test develop (generic) neuro_dmt Validations for the neocortex
release"""
from neuro_dmt.tests.develop.neocortex.analysis import *
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
        ValidationType=\
            self.get_validation_type(
                phenomenon)
        return\
            ValidationType(
                phenomenon=phenomenon,
                adapter=self._adapter,
                animal=self._circuit_model.animal,
                measurement_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                spatial_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                plotted_parameters=[
                    CorticalLayer().label],
                reference_data=ValidationReferenceData.get(phenomenon),
                output_dir_path=self._output_dir_path,
                *args, **kwargs)
               