"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
import os
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
from neuro_dmt.measurement.parameter import HippocampalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainValidation
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry


class BlueBrainCellDensityValidation(
        BlueBrainValidation):
    """..."""
    circuit_geometry=\
        O1CircuitGeometry
    brain_region=\
        brain_regions.hippocampus
    spatial_parameters=\
        {HippocampalLayer()}
    Plotter=\
        BarPlotComparison
    ModelAdapter=\
        BlueBrainModelAdapter
    Validation=\
        CellDensityValidation
    reference_data_path=\
        os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
            "work/validations/dmt",
            "examples/datasets/hippocampus/ca1/mouse",
            Validation.phenomenon.label)
    def reference_data(self):
        """..."""
        return reference_datasets.cell_density(
            self.reference_data_path)
                                       
validation=\
    dict(
        cell_density=BlueBrainCellDensityValidation)
