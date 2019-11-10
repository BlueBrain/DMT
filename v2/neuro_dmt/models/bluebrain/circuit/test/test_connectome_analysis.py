"""
Test using connectome properties.
"""
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    ConnectionProbabilityInterface
from ..mock.circuit import MockCircuit
from ..mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from ..model import BlueBrainCircuitModel
from . import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

logger = Logger(client="test connectome analysis.")
circuit_label = "S1RatSSCxDisseminationBio1"
circuit_model_bio_one = BlueBrainCircuitModel(
    path_circuit_data=get_path_circuit(circuit_label))
mock_circuit_model =\
    BlueBrainCircuitModel(
        MockCircuit.build(
            circuit_composition,
            circuit_connectivity),
        label="BlueBrainCircuitModelMockLight")

def test_connection_probability():
    """
    `BrainCircuitAnalysis` for connection probability should work with
    `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
    """
    phenomenon = Phenomenon(
        "Connection Probability",
        """
        Probability that two neurons in a pathway are connected.
        While mostly interested in `mtype->mtype` pathways, we can define
        a pathway as the group of connected neurons with pre-synaptic and
        post-synaptic neurons belonging to two parametrically defined groups.
        As an example consider neuron populations defined by not only `mtype`
        but also by soma-distance from a given location.
        """,
        group="Connectome")
    number_pathways = 5
    pathways =\
        mock_circuit_model.pathways(frozenset(("mtype",)))\
                          .sample(n=number_pathways)
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=ConnectionProbabilityInterface,
            # measurement_parameters=Parameters(
            #     lambda adapter, model: adapter.get_pathways(
            #         model, ("mtype",)
            #     ).sample(n=number_pathways)),
            measurement_parameters=Parameters(pathways),
            plotter=HeatMap(
                xvar=("pre_synaptic", "mtype"),
                xlabel="pre-mtype",
                yvar=("post_synaptic", "mtype"),
                ylabel="post-mtype",
                vvar=("connection_probability", "mean"))))

    #analysis_test.test_circuit_data_path(mock_circuit_model)
    connection_probability_measurement =\
        analysis_test.test_get_measurement(mock_circuit_model, sample_size=10)
    assert len(connection_probability_measurement) == 1
    dataset, dataframe = [
        (k, v) for k, v in connection_probability_measurement.items()][0]
    assert dataset == mock_circuit_model.label
    summary =\
        measurement.concat_as_summaries(
            connection_probability_measurement)
    assert summary.shape[0] == number_pathways,\
        summary.shape
    
    logger.info(
        logger.get_source_info(),
        "Test call to analysis")
    analysis_test\
        .test_call_analysis(
            mock_circuit_model)
    logger.info(
        logger.get_source_info(),
        "Test post report")
    analysis_test\
        .test_post_report(
            mock_circuit_model,
            sample_size=10,
            output_folder="analysis")

def test_connection_probability_by_distance():
    """
    `BrainCircuitAnalysis` for connection probability should work with
    `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
    """
    phenomenon = Phenomenon(
        "Connection Probability",
        """
        Probability that two neurons in a pathway are connected.
        While mostly interested in `mtype->mtype` pathways, we can define
        a pathway as the group of connected neurons with pre-synaptic and
        post-synaptic neurons belonging to two parametrically defined groups.
        As an example consider neuron populations defined by not only `mtype`
        but also by soma-distance from a given location.
        """,
        group="Connectome")
    number_pathways = 5
    pathways =\
        mock_circuit_model.pathways(frozenset(("mtype",)))\
                          .sample(n=number_pathways)
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=ConnectionProbabilityInterface,
            measurement_parameters=Parameters(pathways),
            plotter=HeatMap(
                xvar=("pre_synaptic", "mtype"),
                xlabel="pre-mtype",
                yvar=("post_synaptic", "mtype"),
                ylabel="post-mtype",
                vvar=("connection_probability", "mean"))))

    #analysis_test.test_circuit_data_path(mock_circuit_model)
    connection_probability_measurement =\
        analysis_test.test_get_measurement(mock_circuit_model, sample_size=10)
    assert len(connection_probability_measurement) == 1
    dataset, dataframe = [
        (k, v) for k, v in connection_probability_measurement.items()][0]
    assert dataset == mock_circuit_model.label
    summary =\
        measurement.concat_as_summaries(
            connection_probability_measurement)
    assert summary.shape[0] == number_pathways,\
        summary.shape
    
    logger.info(
        logger.get_source_info(),
        "Test call to analysis")
    analysis_test\
        .test_call_analysis(
            mock_circuit_model)
    logger.info(
        logger.get_source_info(),
        "Test post report")
    analysis_test\
        .test_post_report(
            mock_circuit_model,
            sample_size=10,
            output_folder="analysis")
