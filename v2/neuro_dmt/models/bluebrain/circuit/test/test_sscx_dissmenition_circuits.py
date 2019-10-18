"""
Test using SSCx dissemination circuits.
"""

import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting.bars import Bars 
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from ..model import BlueBrainCircuitModel
from .import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

circuit_label = "S1RatSSCxDisseminationBio1"
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
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=phenomenon.label,
                ylabel=phenomenon.name,
                gvar="dataset")))

    analysis_test.test_circuit_model(circuit_label)
    analysis_test.test_adapter_methods(circuit_model_bio_one)
        

