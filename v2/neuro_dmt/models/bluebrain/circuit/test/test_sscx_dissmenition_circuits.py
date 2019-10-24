"""
Test using SSCx dissemination circuits.
"""

import numpy as np
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting.bars import Bars 
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from ..model import BlueBrainCircuitModel
from . import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

circuit_label = "S1RatSSCxDisseminationBio0L1AllINH"
circuit_model_bio_one = BlueBrainCircuitModel(
    path_circuit_data=get_path_circuit(circuit_label))

def test_cell_denisty_analysis():
    """
    `BrainCircuitAnalysis` for cell density should work with
    `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="Composition")
    layers = ["L{}".format(layer) for layer in range(1, 7)]
    regions = ["S1HL", "S1FL", "S1Sh", "S1Tr"]
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({
                    "layer": [layer for layer in layers for _ in regions],
                    "region": [region for _ in layers for region in regions]})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=phenomenon.label,
                ylabel=phenomenon.name,
                gvar="dataset")))

    analysis_test.test_circuit_model(circuit_label)
    cell_density_measurement =\
        analysis_test.test_get_measurement(circuit_model_bio_one)
    assert len(cell_density_measurement) == 1
    dataset, dataframe =[
        (k, v) for k, v in cell_density_measurement.items()][0]
    assert dataset == circuit_model_bio_one.label
    summary = measurement.concat_as_summaries(cell_density_measurement)
    assert summary.shape[0] == len(layers) * len(regions), summary.shape

    layer_means = summary.cell_density["mean"]
    # layer_means = [
    #     row.cell_density["mean"]
    #     for _, row in summary.iterrows()]

    assert np.all([m > 0. for m in layer_means]), summary

    analysis_test\
        .test_call_analysis(
            circuit_model_bio_one)
    analysis_test\
        .test_post_report(
            circuit_model_bio_one,
            output_folder="validation")
