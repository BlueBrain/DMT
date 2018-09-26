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
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""
    ModelAdapter = BlueBrainModelAdapter
    def __init__(self, brain_region, with_plotter=None,
                 *args,  **kwargs):
        """..."""
        self.__plotter_type = with_plotter
        super(BlueBrainCellDensityValidation, self)\
            .__init__(brain_region, O1Circuit, *args, **kwargs)

    def get_validation(self, reference_data_path):
        """..."""
        from neuro_dmt.validations.circuit.composition.by_layer \
            import CellDensityValidation
        validation_data = reference_datasets.cell_density(reference_data_path)
        cdv = CellDensityValidation(validation_data=validation_data,
                                    brain_region=self.brain_region,
                                    spatial_parameters={CorticalLayer()},
                                    plotter_type=self.__plotter_type,
                                    adapter=self._adapter)
        return cdv
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
