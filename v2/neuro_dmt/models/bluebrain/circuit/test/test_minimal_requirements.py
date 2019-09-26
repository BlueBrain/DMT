"""
Test cell density analysis.
"""

import pandas as pd
from pathlib import Path
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting.bars import Bars
from dmt.tk.parameters import Parameters
from dmt.tk.reporting import Report, Reporter
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from . import *
from . import mock

def test_mock_circuit_analysis_with_adapter():
    """
    Circuit analysis with adapter set should produce the expected output.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    mock_circuit_model = mock.get_circuit_model()
    mock_adapter = mock.get_circuit_adapter(mock_circuit_model)
    cell_density_analysis =\
        BrainCircuitAnalysis(
            phenomenon=cell_density_phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=cell_density_phenomenon.label,
                ylabel=cell_density_phenomenon.name,
                gvar="dataset"),
            adapter=mock_adapter)
    analysis_test = CircuitAnalysisTest(analysis=cell_density_analysis)
    analysis_test.test_get_measurement(mock_circuit_model)
    analysis_test.test_call_analysis(mock_circuit_model)
    analysis_test.test_post_report(mock_circuit_model)


def test_mock_circuit_analysis_without_adapter():
    """
    Circuit analysis with adapter passed to its methods.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    mock_circuit_model = mock.get_circuit_model()
    mock_adapter = mock.get_circuit_adapter(mock_circuit_model)
    cell_density_analysis =\
        BrainCircuitAnalysis(
            phenomenon=cell_density_phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=cell_density_phenomenon.label,
                ylabel=cell_density_phenomenon.name,
                gvar="dataset"))
    analysis_test = CircuitAnalysisTest(analysis=cell_density_analysis)
    analysis_test.test_get_measurement(mock_circuit_model, mock_adapter)
    analysis_test.test_call_analysis(mock_circuit_model, mock_adapter)
    analysis_test.test_post_report(mock_circuit_model, mock_adapter)
