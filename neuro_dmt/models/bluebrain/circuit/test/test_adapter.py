"""
Test adapter for Blue Brain circuit models.
"""

import numpy as np
import pandas as pd
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.collections import take
from neuro_dmt import terminology
from neuro_dmt.models.bluebrain.circuit.model import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainCircuitAdapter
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces\
    import CellDensityAdapterInterface
from neuro_dmt.terminology import measurement_method
from neuro_dmt.models.bluebrain.circuit.test import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

cell_density_phenomenon =\
    Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")

adapter = BlueBrainCircuitAdapter()

def test_cell_density():
    """
    Adapter should be able get cell densities from the model.
    """
    circuit_label = "S1RatSSCxDisseminationBio0L1AllINH"
    phenomenon = Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="Composition")
    layers = ["L{}".format(layer) for layer in range(1, 7)]
    regions = ["S1HL", "S1FL", "S1Sh", "S1Tr"]
    measurement_parameters = Parameters(
        pd.DataFrame({
            "layer": [layer for layer in layers for _ in regions],
            "region": [region for _ in layers for region in regions]}))
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=measurement_parameters,
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=phenomenon.label,
                ylabel=phenomenon.name,
                gvar="dataset")))
    measurement_exhaustive = pd.Series(
        analysis_test.test_adapter_method(
            circuit_label,
            analysis_test.adapter.get_cell_density,
            measurement_parameters.values,
            measurement_method=terminology.sampling_methodology.exhaustive),
        name="cell_density")
    exhaustive = pd\
        .concat(
            [measurement_parameters.values, measurement_exhaustive],
            axis=1)\
        .set_index(["region", "layer"])
    sampling_parameters = pd.DataFrame(
        measurement_parameters.for_sampling(size=20))
    measurement_samples = pd.Series(
        analysis_test.test_adapter_method(
            circuit_label,
            analysis_test.adapter.get_cell_density,
            sampling_parameters,
            measurement_method=terminology.sampling_methodology.random),
        name="cell_density")
    samples = pd\
        .concat(
            [sampling_parameters, measurement_samples],
            axis=1)\
        .set_index(["region", "layer"])
    return samples, exhaustive
