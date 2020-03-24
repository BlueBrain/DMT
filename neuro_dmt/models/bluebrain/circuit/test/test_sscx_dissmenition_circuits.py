"""
Test using SSCx dissemination circuits.
"""

import numpy as np
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.data import rat
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
    layers =[
        "L{}".format(layer) for layer in range(1, 7)]
    regions =[
        "S1HL", "S1FL", "S1Sh", "S1Tr"]
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({
                    "region": [region for _ in layers for region in regions],
                    "layer": [layer for layer in layers for _ in regions]})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=phenomenon.label,
                ylabel=phenomenon.name,
                gvar="dataset")))

    #analysis_test.test_circuit_model(circuit_label)
    cell_density_measurement =\
        analysis_test.test_get_measurement(circuit_model_bio_one)
    assert len(cell_density_measurement) == 1
    dataset, dataframe =[
        (k, v) for k, v in cell_density_measurement.items()][0]
    assert dataset == circuit_model_bio_one.label
    summary = measurement.concat_as_summaries(cell_density_measurement)
    assert summary.shape[0] == len(layers) * len(regions), summary.shape

    layer_means = summary.cell_density["mean"]

    assert np.all([m > 0. for m in layer_means]), summary

    analysis_test\
        .test_call_analysis(
            circuit_model_bio_one)
    analysis_test\
        .test_post_report(
            circuit_model_bio_one,
            output_folder="analyses")

def test_cell_density_validation():
    """
    `BrainCircuitAnalysis` for cell density should work with
    `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="Composition")
    layers =[
        "L{}".format(layer) for layer in range(1, 7)]
    regions =[
        "S1HL", "S1FL", "S1Sh", "S1Tr"]
    reference_datasets = dict(
        DeFelipe2017=rat.defelipe2017.summary_measurement.samples(1000),
        DeFelipe2014=rat.defelipe2014.summary_measurement.samples(1000),
        meyer2010=rat.meyer2010.samples(1000))
    validation_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            reference_data=reference_datasets,
            measurement_parameters=Parameters(
                pd.DataFrame({
                    "region": [region for _ in layers for region in regions],
                    "layer": [layer for layer in layers for _ in regions]})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=phenomenon.label,
                ylabel=phenomenon.name,
                gvar="dataset")))

    #validation_test.test_circuit_model(circuit_label)
    cell_density_measurement =\
        validation_test.test_get_measurement(
            circuit_model_bio_one,
            sample_size=100)
    assert len(cell_density_measurement) == 1 + len(reference_datasets)
    dataset, dataframe =[
        (k, v) for k, v in cell_density_measurement.items()][0]
    assert dataset == circuit_model_bio_one.label
    summary = measurement.concat_as_summaries(cell_density_measurement)
    number_expected_rows =\
        len(layers) * len(regions)\
        + len(layers) * len(reference_datasets)
    assert summary.shape[0] == number_expected_rows, summary.shape

    layer_means = summary.cell_density["mean"]

    assert np.all([m > 0. for m in layer_means]), summary

    validation_test\
        .test_call_analysis(
            circuit_model_bio_one)
    validation_test\
        .test_post_report(
            circuit_model_bio_one,
            output_folder="validation")

# def test_connection_probability_analysis():
#     """
#     `BrainCircuitAnalysis` for connection probability should work with
#     `BlueBrainCircuitModel` and `BlueBrainCircuitaAapter`
#     """
#     phenomenon = Phenomenon(
#         "Connection Probability",
#         """
#         Probability that two neurons in a pathway are connected.
#         mostly we will use `mtype`-->`mtype` pathways. but we could define
#         connection probability of `synapse_class`-->`synapse_class` pathways
#         as well.
#         """,
#         group="Connectome")
#     analysis_test = BlueBrainCircuitAnalysisTest(
#         analysis=BrainCircuitAnalysis(
#             phenomenon=Phenomenon,
#             AdapterInterface=ConnectionProbabilityAdapterInterface,
#             measurement_parameters=Parameters(
#                 lambda model, adapter: adapter.get_mtypes(model)),
#             plotter=HeatMap(
#                 xvar="pre_mtype",
#                 xlabel="pre-mtype",
#                 yvar="post_mtype",
#                 ylabel="post-mtype",
#                 vvar=("connection_probability", "mean"))))
#     analysis_test\
#         .test_circuit_model(circuit_label)
#     connection_probability_measurement =\
#         analysis_test.test_get_measurement(
#             circuit_model_bio_one)
#     assert len(connection_probability_measurement) == 1
#     dataset, dataframe =[
#         (k, v) for k, v in connection_probability_measurement.items()][0]
#     assert dataset = circuit_model_bio_one.label
#     summary =\
#         measurement.concat_as_summaries(
#             connection_probability_measurement)
#     mtypes =\
#         analysis_test.adapter\
#                      .get_mtypes(
#                          circuit_model_bio_one)
#     assert summary.shape[0] == len(mtypes) * len(mtypes), summary.shape

#     analysis_test\
#         .test_call_analysis(
#             circuit_model_bio_one)
#     analysis_test\
#         .test_post_report(
#             circuit_model_bio_one,
#             output_folder="analysis")
