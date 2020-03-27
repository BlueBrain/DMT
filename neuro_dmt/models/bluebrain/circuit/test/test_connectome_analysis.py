# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test using connectome properties.
"""
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap, LinePlot
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    ConnectionProbabilityInterface,\
    ConnectionProbabilityBySomaDistanceInterface,\
    AfferentConnectionCountBySomaDistanceInterface,\
    AfferentConnectionCountInterface
from ..mock.circuit import MockCircuit
from ..mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from ..model import BlueBrainCircuitModel
from ..model.cell_type import CellType
from ..adapter import BlueBrainCircuitAdapter
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

# def test_connection_probability():
#     """
#     `BrainCircuitAnalysis` for connection probability should work with
#     `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
#     """
#     phenomenon = Phenomenon(
#         "Connection Probability",
#         """
#         Probability that two neurons in a pathway are connected.
#         While mostly interested in `mtype->mtype` pathways, we can define
#         a pathway as the group of connected neurons with pre-synaptic and
#         post-synaptic neurons belonging to two parametrically defined groups.
#         As an example consider neuron populations defined by not only `mtype`
#         but also by soma-distance from a given location.
#         """,
#         group="Connectome")
#     number_pathways = 5
#     pathways =\
#         mock_circuit_model.pathways(frozenset(("mtype",)))\
#                           .sample(n=number_pathways)
#     analysis_test = BlueBrainCircuitAnalysisTest(
#         analysis=BrainCircuitAnalysis(
#             phenomenon=phenomenon,
#             AdapterInterface=ConnectionProbabilityInterface,
#             # measurement_parameters=Parameters(
#             #     lambda adapter, model: adapter.get_pathways(
#             #         model, ("mtype",)
#             #     ).sample(n=number_pathways)),
#             measurement_parameters=Parameters(pathways),
#             plotter=HeatMap(
#                 xvar=("pre_synaptic", "mtype"),
#                 xlabel="pre-mtype",
#                 yvar=("post_synaptic", "mtype"),
#                 ylabel="post-mtype",
#                 vvar=("connection_probability", "mean"))))

#     #analysis_test.test_circuit_data_path(mock_circuit_model)
#     connection_probability_measurement =\
#         analysis_test.test_get_measurement(mock_circuit_model, sample_size=2)
#     assert len(connection_probability_measurement) == 1
#     dataset, dataframe = [
#         (k, v) for k, v in connection_probability_measurement.items()][0]
#     assert dataset == mock_circuit_model.label
#     summary =\
#         measurement.concat_as_summaries(
#             connection_probability_measurement)
#     assert summary.shape[0] == number_pathways,\
#         summary.shape
    
#     logger.info(
#         logger.get_source_info(),
#         "Test call to analysis")
#     analysis_test\
#         .test_call_analysis(
#             mock_circuit_model)
#     logger.info(
#         logger.get_source_info(),
#         "Test post report")
#     analysis_test\
#         .test_post_report(
#             mock_circuit_model,
#             sample_size=10,
#             output_folder="analyses")

# def test_connection_probability_by_soma_distance():
#     """
#     `BrainCircuitAnalysis` for connection probability should work with
#     `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
#     """
#     phenomenon = Phenomenon(
#         "Connection Probability",
#         """
#         Probability that two neurons in a pathway are connected.
#         While mostly interested in `mtype->mtype` pathways, we can define
#         a pathway as the group of connected neurons with pre-synaptic and
#         post-synaptic neurons belonging to two parametrically defined groups.
#         As an example consider neuron populations defined by not only `mtype`
#         but also by soma-distance from a given location.
#         """,
#         group="Connectome")
#     adapter =\
#         BlueBrainCircuitAdapter()
#     cell_types =\
#         pd.DataFrame([
#             {"mtype": "L23_MC"},
#             {"mtype": "L6_TPC:A"},
#             {"mtype": "L5_TPC:A"},
#             {"mtype": "L5_MC"},
#             {"mtype":"L6_ChC"}])
#     pathways =\
#         adapter.get_pathways(
#             mock_circuit_model,
#             cell_group=cell_types)
#     analysis_test = BlueBrainCircuitAnalysisTest(
#         analysis=BrainCircuitAnalysis(
#             phenomenon=phenomenon,
#             AdapterInterface=ConnectionProbabilityBySomaDistanceInterface,
#             measurement_parameters=Parameters(pathways),
#             measurement_collection=measurement.collection.series_type,
#             plotter=LinePlot(
#                 xvar="soma_distance",
#                 xlabel="Soma Distance",
#                 yvar="connection_probability",
#                 ylabel="Connection Probability",
#                 gvar=("pre_synaptic", "mtype"),
#                 fvar=("post_synaptic", "mtype"))))

#     logger.info(
#         logger.get_source_info(),
#         "Test get measurement")
#     connection_probability_measurement =\
#         analysis_test.test_get_measurement(mock_circuit_model, sample_size=2)
#     assert len(connection_probability_measurement) == 1
#     dataset, dataframe = [
#         (k, v) for k, v in connection_probability_measurement.items()][0]
#     assert dataset == mock_circuit_model.label
#     summary =\
#         measurement.concat_as_summaries(
#             connection_probability_measurement)
#     without_soma_distance =\
#         summary.groupby(list(pathways.columns.values))\
#                .agg("size")
            
#     assert without_soma_distance.shape[0] == pathways.shape[0],\
#         (without_soma_distance.shape[0], pathways.shape[0])
    
#     logger.info(
#         logger.get_source_info(),
#         "Test call to analysis")
#     analysis_test\
#         .test_call_analysis(
#             mock_circuit_model)
#     logger.info(
#         logger.get_source_info(),
#         "Test post report")
#     analysis_test\
#         .test_post_report(
#             mock_circuit_model,
#             sample_size=10,
#             output_folder="analyses")

# def test_number_connections_afferent_by_soma_distance():
#     """
#     `BrainCircuitAnalysis` for connection probability should work with
#     `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
#     """
#     phenomenon = Phenomenon(
#         "Afferent Connection Count",
#         """
#         Number of afferent connections incident at a post-synaptic cell.
#         While mostly interested in `mtype->mtype` pathways, we can define
#         a pathway as the group of connected neurons with pre-synaptic and
#         post-synaptic neurons belonging to two parametrically defined groups.
#         As an example consider neuron populations defined by not only `mtype`
#         but also by soma-distance from a given location.
#         """,
#         group="Connectome")
#     adapter =\
#         BlueBrainCircuitAdapter()
#     cell_types =\
#         pd.DataFrame([
#             {"mtype": "L23_MC"},
#             {"mtype": "L6_TPC:A"},
#             {"mtype": "L5_TPC:A"},
#             {"mtype": "L5_MC"},
#             {"mtype":"L6_ChC"}])
#     pathways =\
#         adapter.get_pathways(
#             mock_circuit_model,
#             cell_group=cell_types)
#     analysis_test = BlueBrainCircuitAnalysisTest(
#         analysis=BrainCircuitAnalysis(
#             phenomenon=phenomenon,
#             AdapterInterface=AfferentConnectionCountBySomaDistanceInterface,
#             measurement_parameters=Parameters(pathways),
#             measurement_collection=measurement.collection.series_type,
#             plotter=LinePlot(
#                 xvar="soma_distance",
#                 xlabel="Soma Distance",
#                 yvar="afferent_connection_count",
#                 ylabel="Mean number of afferent connections",
#                 gvar=("pre_synaptic", "mtype"),
#                 fvar=("post_synaptic", "mtype"),
#                 drawstyle="steps-mid")))

#     logger.info(
#         logger.get_source_info(),
#         "Test get measurement")
#     afferent_count_measurement =\
#         analysis_test.test_get_measurement(mock_circuit_model, sample_size=2)
#     assert len(afferent_count_measurement) == 1
#     dataset, dataframe = [
#         (k, v) for k, v in afferent_count_measurement.items()][0]
#     assert dataset == mock_circuit_model.label
#     summary =\
#         measurement.concat_as_summaries(
#             afferent_count_measurement)
#     without_soma_distance =\
#         summary.groupby(list(pathways.columns.values))\
#                .agg("size")
            
#     assert without_soma_distance.shape[0] == pathways.shape[0],\
#         (without_soma_distance.shape[0], pathways.shape[0])
    
#     logger.info(
#         logger.get_source_info(),
#         "Test call to analysis")
#     analysis_test\
#         .test_call_analysis(
#             mock_circuit_model)
#     logger.info(
#         logger.get_source_info(),
#         "Test post report")
#     analysis_test\
#         .test_post_report(
#             mock_circuit_model,
#             sample_size=10,
#             output_folder="analyses")

def test_afferent_connection_count():
    """
    `BrainCircuitAnalysis` for connection probability should work with
    `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter`
    """
    phenomenon = Phenomenon(
        "Afferent Connection Count",
        """
        Number of afferent connections incident at a post-synaptic cell.
        While mostly interested in `mtype->mtype` pathways, we can define
        a pathway as the group of connected neurons with pre-synaptic and
        post-synaptic neurons belonging to two parametrically defined groups.
        As an example consider neuron populations defined by not only `mtype`
        but also by soma-distance from a given location.
        """,
        group="Connectome")
    adapter =\
        BlueBrainCircuitAdapter()
    post_synaptic_cell_types =\
        pd.DataFrame({
            ("post_synaptic", "mtype"): [
                "L23_MC", "L6_TPC:A", "L5_TPC:A", "L5_MC", "L6_ChC"]
        })
    analysis_test = BlueBrainCircuitAnalysisTest(
        analysis=BrainCircuitAnalysis(
            phenomenon=phenomenon,
            AdapterInterface=AfferentConnectionCountInterface,
            measurement_parameters=Parameters(post_synaptic_cell_types),
            measurement_collection=measurement.collection.series_type,
            plotter=LinePlot(
                xvar="soma_distance",
                xlabel="Soma Distance",
                yvar="afferent_connection_count",
                ylabel="Mean number of afferent connections",
                gvar=("pre_synaptic", "mtype"),
                fvar=("post_synaptic", "mtype"),
                drawstyle="steps-mid")))

    logger.info(
        logger.get_source_info(),
        "Test get measurement")
    afferent_count_measurement =\
        analysis_test.test_get_measurement(mock_circuit_model, sample_size=2)
    assert len(afferent_count_measurement) == 1
    dataset, dataframe = [
        (k, v) for k, v in afferent_count_measurement.items()][0]
    assert dataset == mock_circuit_model.label
    
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
            output_folder="analyses")
