"""
Test using connectome properties.
"""
import numpy as np
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    ConnectionProbabilityInterface
from ..model import BlueBrainCircuitModel
from . import\
    BlueBrainCircuitAnalysisTest,\
    get_path_circuit

circuit_label = "S1RatSSCxDisseminationBio1"
circuit_model_bio_one = BlueBrainCircuitModel(
    path_circuit_data=get_path_circuit(circuit_label))


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
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=ConnectionProbabilityInterface,
            measurement_parameters=Parameters(
                lambda adapter, model: adapter.get_pathways(model).sample(n=20)),
            plotter=HeatMap(
                xvar="pre_mtype",
                xlabel="pre-mtype",
                yvar="post_mtype",
                ylabel="post-mtype",
                vvar=("connection_probability", "mean"))))

    analysis_test.test_circuit_model(circuit_label)
    connection_probability_measurement =\
        analysis_test.test_get_measurement(circuit_model_bio_one)
    assert len(connection_probability_measurement) == 1
    dataset, dataframe = [
        (k, v) for k, v in connection_probability_measurement.items()][0]
    assert dataset == circuit_model_bio_one.label
    summary =\
        measurement.concat_as_summaries(
            connection_probability_measurement)
    mtypes =\
        analysis_test.adapter\
                     .get_mtypes(circuit_model_bio_one)
    assert summary.shape[0] == len(mtypes) * len(mtypes),\
        summary.shape

    analysis_test\
        .test_call_analysis(
            circuit_model_bio_one)

    analysis_test\
        .test_post_report(
            circuit_model_bio_one,
            output_folder="analysis")
