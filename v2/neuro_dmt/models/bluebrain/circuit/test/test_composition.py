
"""
Test `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter` with composition
analyses and validations.
"""
import numpy as np
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap
from dmt.tk.plotting.multi import MultiPlot
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.data import rat
from ..model import BlueBrainCircuitModel
from ..mock.circuit import MockBlueBrainCircuitModel
from ..mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from . import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

mock_circuit_model =\
    MockBlueBrainCircuitModel(
        circuit_composition,
        circuit_connectivity,
        label="BlueBrainCircuitModelMockLight")

def test_cell_density():
    """
    Should be able to analyze cell densities.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        "Number of cells in a unit volume.",
        group="Composition"
    )
    layers =[
        "L{}".format(layer) for layer in range(1, 7)
    ]
    regions =[
        "S1HL", "S1FL", "S1Sh", "S1Tr"
    ]
    def _append_region(reference_dataframe):
        return pd.concat([
            reference_dataframe\
            .reset_index()\
            .assign(region=region)\
            .set_index(["region", "layer"])
            for region in regions])
    
    reference_data =\
        dict(
            DeFelipe2017=_append_region(
                rat.defelipe2017.summary_measurement.samples(1000)),
            DeFelipe2014=_append_region(
                rat.defelipe2014.summary_measurement.samples(1000)),
            meyer2010=_append_region(
                rat.meyer2010.samples(1000)))
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            reference_data=reference_data,
            measurement_parameters=Parameters(
                pd.DataFrame({
                    "region": [
                        region
                        for _ in layers
                        for region in regions],
                    "layer": [
                        layer
                        for layer in layers
                        for _ in regions]})),
            plotter=MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="dataset"))))

    cell_density_measurement =\
        analysis_test.test_get_measurement(
            mock_circuit_model,
            sample_size=10)

    assert len(cell_density_measurement) == 1 + len(reference_data),\
        """
        observed {}
        expected {}
        """.format(
            len(cell_density_measurement),
            1 + len(reference_data))
    dataset, dataframe =[
        (k, v) for k, v in cell_density_measurement.items()][0]

    assert dataset == mock_circuit_model.label
    summary =\
        measurement.concat_as_summaries(
            cell_density_measurement)
    number_expected_rows =\
        len(layers) * len(regions)\
        * (1. + len(reference_data))
    assert summary.shape[0] == number_expected_rows,\
        (summary.shape, number_expected_rows)

    layer_means = summary.cell_density["mean"]

    assert np.all([m > 0. for m in layer_means]), summary

    analysis_test\
        .test_call_analysis(
            mock_circuit_model)

    analysis_test\
        .test_post_report(
            mock_circuit_model,
            output_folder="validations")


