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
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit
    

circuit_config_path\
    = os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj42/circuits",
        "O1",
        "20180219",
        "CircuitConfig")

logger = Logger(client=__name__, level=Logger.level.TEST)

circuit_model\
    = Circuit(circuit_config_path)


bbma\
    = BlueBrainModelAdapter(
        brain_region=brain_regions.hippocampus,
        circuit_build=O1Circuit,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico")

ca1_density\
    = bbma.get_cell_density(
        circuit_model)
ca1_density.data.index\
    = pd.Index(
        ["CA1"],
        dtype="object",
        name="cell_type")
sp_pc_density\
    = bbma.get_cell_density(
        circuit_model,
        region="SP",
        morph_class="PYR")
sp_pc_density.data.index\
    = pd.Index(
        ["SP_PC"],
        dtype="object",
        name="cell_type")
hippocampal_layer\
    = HippocampalLayer()
layer_density\
    = bbma.get_cell_density(
        circuit_model,
        {hippocampal_layer})
layer_density.data.index\
    = pd.Index(
        [hippocampal_layer.repr(i)
         for i in layer_density.data.index],
        dtype=object,
        name="cell_type")
measurement\
    = layer_density
measurement.data\
    = pd.concat([
        ca1_density.data,
        sp_pc_density.data,
        layer_density.data])

def run(validation_name, plotter=BarPlotComparison):
    """..."""
    logger.info("Will run validation {}".format(validation_name))
    validation = composition.validation[validation_name]()
    logger.info(
        logger.get_source_info(),
        "validation type {}".format(validation.__class__)
    )
    return validation(reference_data_path(validation_name), circuit_config_path)
                      
