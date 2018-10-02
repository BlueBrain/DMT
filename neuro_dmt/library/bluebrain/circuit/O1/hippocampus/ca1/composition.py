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
    circuit_build = O1Circuit
    brain_region = brain_regions.hippocampus
    spatial_parameters = {HippocampalLayer()}
    plotter_type = BarPlotComparison
    ModelAdapter = BlueBrainModelAdapter
    Validation = CellDensityValidation

    @staticmethod
    def get_reference_data(reference_data_path):
        """..."""
        return reference_datasets.cell_density(reference_data_path)
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
