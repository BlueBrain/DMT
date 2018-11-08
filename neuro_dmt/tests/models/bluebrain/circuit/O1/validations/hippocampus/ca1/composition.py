"""Test develop cell density validation."""
import sys
import os
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison
from dmt.vtk.utils.logging import Logger, with_logging
#from neuro_dmt.library.bluebrain.circuit.O1.hippocampus.ca1 import composition
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter\
    import HippocampalLayerSLM_SR_Fused, HippocampalLayer
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.analysis.circuit.composition.by_region.hippocampus.cell_density\
    import CellCompositionAnalysis
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import HippocampalFakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry, SSCxCorticalO1Specialization

circuit_config_path\
    = os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj42/circuits",
        "O1",
        "20180904",
        "CircuitConfig")


class HippocampalO1Specialization(
        SSCxCorticalO1Specialization):
    def query_param(self, param):
        if param == 'layer':
            return 'region'
        return param


class HippocampalO1CircuitGeometry(
        O1CircuitGeometry):
    """O1CircuitGeometry whose 'circuit_specialization' is already set."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.circuit_specialization\
            = HippocampalO1Specialization(
                *args, **kwargs)
        super().__init__(
            *args, **kwargs)

    
logger\
    = Logger(
        client=__name__,
        level=Logger.level.TEST)
circuit_model\
    = Circuit(
        circuit_config_path)
bbma\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.hippocampus,
        circuit_geometry_type=HippocampalFakeAtlasCircuitGeometry,
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
