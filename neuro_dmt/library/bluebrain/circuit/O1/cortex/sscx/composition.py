"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
from dmt.vtk.utils.collections import Record
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.parameters import CorticalLayer


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""
    def __init__(self, *args, with_plotter=None, **kwargs):
        """..."""
        self.__plotter_type = with_plotter
        super(BlueBrainCellDensityValidation, self).__init__(*args, **kwargs)

    model_adapter = BlueBrainModelAdapter
    def get_validation(self, reference_data_path):
        """..."""
        from neuro_dmt.validations.circuit.composition.by_layer \
            import CellDensityValidation
        validation_data = reference_datasets.cell_density(reference_data_path)
        self._adapter._spatial_parameter = CorticalLayer
        cdv = CellDensityValidation(validation_data, adapter=self._adapter)
        if self.__plotter_type:
            cdv.plotter_type = self.__plotter_type
        return cdv
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
