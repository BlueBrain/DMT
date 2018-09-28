"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import HippocampalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer \
    import reference_datasets
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.parameters import HippocampalLayer


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""
    ModelAdapter = BlueBrainModelAdapter
    def __init__(self, plotter_type=None,
                 *args,  **kwargs):
        """..."""
        super().__init__(brain_regions.hippocampus, O1Circuit,
                         plotter_type=plotter_type
                         *args, **kwargs)
            
    def get_validation(self, reference_data_path):
        """..."""
        from neuro_dmt.validations.circuit.composition.by_layer \
            import CellDensityValidation
        validation_data = reference_datasets.cell_density(reference_data_path)
        cdv = CellDensityValidation(validation_data=validation_data,
                                    brain_region=brain_regions.cortex
                                    spatial_parameters={HippocampalLayer()},
                                    plotter_type=self._plotter_type,
                                    adapter=self._adapter)
        return cdv
                                     
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
