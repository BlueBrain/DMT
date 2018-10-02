"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
from dmt.vtk.utils.collections import Record
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit
from neuro_dmt.validations.circuit.composition.by_layer \
    import CellDensityValidation


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""
    circuit_build = O1Circuit
    brain_region = brain_regions.cortex
    spatial_parameters = {CorticalLayer()}
    plotter_type = BarPlotComparison
    ModelAdapter = BlueBrainModelAdapter
    Validation = CellDensityValidation

    @staticmethod
    def get_reference_data(reference_data_path):
        """..."""
        return reference_datasets.cell_density(reference_data_path)
                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
