"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
import os
from dmt.vtk.utils.collections import Record
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.data.reference import MultiReferenceData
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainCompositionValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit


class BlueBrainCellDensityValidation(BlueBrainCompositionValidation):
    """..."""
    circuit_build = O1Circuit
    plotter_type = BarPlotComparison
    ModelAdapter = BlueBrainModelAdapter

    brain_region = brain_regions.cortex
    spatial_parameters = {CorticalLayer()}
    Validation = CellDensityValidation
    reference_data_path = os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                       "work/validations/dmt",
                                       "examples/datasets/cortex/sscx/rat",
                                       Validation.phenomenon.label)

    @property
    def reference_data(self):
        """..."""
        return reference_datasets.cell_density(self.reference_data_path)

                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
