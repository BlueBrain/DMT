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
from . import mock
from . import CircuitAnalysisTest
from neuro_dmt.data import rat

def test_mock_circuit_analysis_with_adapter():
    """
    Circuit analysis with adapter already set should produce the expected
    output.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    #mock_circuit_model = mock.get_circuit_model()
    mock_circuit_model = None
    mock_adapter = mock.get_circuit_adapter()
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
    assert cell_density_phenomenon.label == "cell_density",\
        "{} not good label".format(cell_density_phenomenon.label)
    #mock_circuit_model = mock.get_circuit_model()
    mock_circuit_model = None
    mock_adapter = mock.get_circuit_adapter()
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


def test_analysis_suite_for_mocks():
    """
    Analysis suite should work as expected, examplified with mock circuit
    and adapter.
    """
    circuit_model =\
        None
    #    mock.get_circuit_model()
    mock_analysis_suite =\
        CircuitAnalysisTest.suite_mock(circuit_model)
    for phenomenon, analysis in mock_analysis_suite.analyses.items():
        assert not isinstance(analysis, str)
        assert analysis.adapter
        analysis_test = CircuitAnalysisTest(analysis=analysis)
        analysis_test.test_get_measurement(circuit_model)
        analysis_test.test_call_analysis(circuit_model)
        analysis_test.test_post_report(circuit_model)


def test_mock_circuit_validation():
    """
    Circuit analysis should be able to validate against reference data.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    assert cell_density_phenomenon.label == "cell_density",\
        "{} not good label".format(cell_density_phenomenon.label)
    mock_circuit_model =\
        None
#        mock.get_circuit_model()
    mock_adapter =\
        mock.get_circuit_adapter(mock_circuit_model)
    reference_datasets =\
        pd.concat([
            rat.defelipe2017\
               .summary_measurement\
               .samples(1000)\
               .assign(dataset="DeFelipe2017"),
            rat.defelipe2014\
               .summary_measurement\
               .samples(1000)\
               .assign(dataset="DeFelipe2014"),
            rat.meyer2010\
               .samples(1000)\
               .assign(dataset="Meyer2010")])\
          .reset_index()\
          .set_index(["dataset", "layer"])
    cell_density_analysis =\
        BrainCircuitAnalysis(
            phenomenon=cell_density_phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            reference_data=reference_datasets,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=cell_density_phenomenon.label,
                ylabel=cell_density_phenomenon.name,
                gvar="dataset"),
            adapter=mock_adapter)
    assert hasattr(cell_density_analysis, "reference_data")
    assert not cell_density_analysis.reference_data.empty
    datasets =\
        cell_density_analysis\
        .reference_data\
        .reset_index()\
        .dataset\
        .unique()
    assert "DeFelipe2017" in datasets, "In {}".format(datasets)
    analysis_test =\
        CircuitAnalysisTest(analysis=cell_density_analysis)
    analysis_test\
        .test_get_measurement(
            mock_circuit_model,
            mock_adapter,
            expected_datasets=[
                "mock_circuit",
                "DeFelipe2017"])
    analysis_test\
        .test_call_analysis(mock_circuit_model, mock_adapter)
    analysis_test\
        .test_post_report(
            mock_circuit_model,
            mock_adapter,
            output_folder="validations")
