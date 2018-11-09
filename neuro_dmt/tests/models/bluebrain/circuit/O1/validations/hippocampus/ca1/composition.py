"""Test develop cell density validation."""
import sys
import os
import numpy as np
import pandas as pd
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter\
    import HippocampalLayerSLM_SR_Fused, HippocampalLayer, Column
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.analysis.circuit.composition.by_region.hippocampus.cell_density\
    import CellCompositionAnalysis
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasBasedLayeredCircuitSpecialization
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import FakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import FakeAtlasBasedCircuitModel

circuit_config_path\
    = os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj42/circuits",
        "O1",
        "20180904",
        "CircuitConfig")


class HippocampalAtlasSpecialization(
        AtlasBasedLayeredCircuitSpecialization):
    """This CircuitSpecialization is for a particular Hippocampus circuit,
    circa 201809DD, and particularly the circuit at
    '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/CircuitConfig'.
    We will put a copy of this class in our validation/analysis library.
    """
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.representative_region\
            = "mc2"
        self.atlas_acronym_separator\
            = ";"
        self.brain_region\
            = kwargs.get(
                "brain_region",
                brain_regions.hippocampus)
        super().__init__(
            *args, **kwargs)

    def get_spanning_column_parameter(self,
            column_values=range(7)):
        """..."""
        return\
            Column(
                value_type=str,
                values=["mc{}".format(n)
                        for n in column_values])
    
class HippocampalFakeAtlasCircuitGeometry(
        FakeAtlasCircuitGeometry):
    """FakeAtlasCircuitGeometry whose 'circuit_specialization' has already
    been set to 'HippocampalAtlasSpecialization'"""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization\
            = HippocampalAtlasSpecialization(
                *args, **kwargs)
        super().__init__(
            circuit,
            *args, **kwargs)
 
    
logger\
    = Logger(
        client=__name__,
        level=Logger.level.TEST)
circuit_model\
    = FakeAtlasBasedCircuitModel(
        animal="mouse",
        brain_region=brain_regions.ca1,
        geometry_type=HippocampalFakeAtlasCircuitGeometry,
        circuit_config=circuit_config_path)
bbma\
    = BlueBrainModelAdapter(
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")
hippocampal_layer\
    = HippocampalLayerSLM_SR_Fused()
cell_composition_analysis\
    = CellCompositionAnalysis(
        animal="rat",
        spatial_parameters={hippocampal_layer},
        adapter=bbma)
cell_composition_measurement\
    = cell_composition_analysis.get_measurement(
        circuit_model)
