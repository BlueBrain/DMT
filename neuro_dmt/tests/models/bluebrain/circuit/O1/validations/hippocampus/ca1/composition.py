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
from neuro_dmt.measurement.parameter import HippocampalLayer
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.random_variate import \
    RandomRegionOfInterest
from neuro_dmt.analysis.circuit.composition.by_region.hippocampus.cell_density\
    import CellCompositionAnalysis
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
    

circuit_config_path\
    = os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj42/circuits",
        "O1",
        "20180219",
        "CircuitConfig")
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
        circuit_geometry=O1CircuitGeometry,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")
hippocampal_layer\
    = HippocampalLayer()

cca = CellCompositionAnalysis(
    animal="rat",
    spatial_parameters={hippocampal_layer},
    adapter=bbma)
measurement = cca.get_measurement(circuit_model)
