"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer \
    import reference_datasets
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.parameters import HippocampalLayer


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""
    model_adapter = BlueBrainModelAdapter
    def get_validation(self, reference_data_path):
        """..."""
        from neuro_dmt.validations.circuit.composition.by_layer \
            import CellDensityValidation
        validation_data = reference_datasets.cell_density(reference_data_path)
        self._adapter._spatial_parameter = HippocampalLayer
        return CellDensityValidation(validation_data, adapter=self._adapter)
                                     
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
