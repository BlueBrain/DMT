# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test and develop code defining concepts and handling pathways.
"""

import numpy as np
import pandas as pd
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from neuro_dmt.models.bluebrain.circuit.mock.circuit import\
    MockCircuit
from neuro_dmt.models.bluebrain.circuit.model.cell_type import\
    CellType
from neuro_dmt.models.bluebrain.circuit.model.pathway import\
    Pathway, GroupByVariables

class TestCircuit():
    """
    A collection of  test circuits to work with.
    """
    mock_circuit = MockCircuit.build(
        circuit_composition,
        circuit_connectivity)
    mock_circuit_model = BlueBrainCircuitModel(
        mock_circuit,
        label="BlueBrainCircuitModelMock")


def test_call_with_groupby_variables():
    """
    `PathwayProperty` should return a dataframe 
    if variables to group by are provided.
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    result =\
        conn_prob(
            groupby=GroupByVariables(
                pre_synaptic_cell_type_specifier={"mtype"},
                post_synaptic_cell_type_specifier={"mtype"}))
    assert isinstance(result, pd.DataFrame)
    assert "pre_synaptic_mtype" in result.index.names
    assert "post_synaptic_mtype" in result.index.names
    assert ("pairs_total") in result.columns
    assert ("pairs_connected") in result.columns
    assert ("connection_probability") in result.columns

def test_call_with_dataframes_input():
    """
    `PathwayProperty.__call__` should return a float
    when the query input is
        pre_synaptic_cell_group : pandas.DataFrame
        post_synaptic_cell_group: pandas.DataFrame
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    post_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    result = conn_prob(
        pre_synaptic_cell_group=pre_synaptic_cells,
        post_synaptic_cell_group=post_synaptic_cells)

    assert isinstance(result, (np.float, float))
    assert result < 1.

def test_get_summary_with_dataframes_input():
    """
   `PathwayProperty.get_summary(...)` should return a pandas.Series
    when the input is
        `pre_synaptic_cell_group` : `pandas.DataFrame`
        `post_synaptic_cell_group`: `pandas.DataFrame`
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    post_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    result = conn_prob.get_summary(
        pre_synaptic_cells,
        post_synaptic_cells)
    assert isinstance(result, pd.Series), result
    assert result.pairs_total == 10000, result
    assert result.pairs_connected < 10000, result
    assert result.connection_probability < 1., result

def test_call_with_series_input():
    """
    `PathwayProperty.__call__` should return a float
    when the query input is
        pre_synaptic_cell_group: pandas.Series
        post_synaptic_cell_group: pandas.Series
    And should cache the results if specified at initialization
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cell_type =\
        pd.Series({"mtype": "L23_MC"})
    post_synaptic_cell_type =\
        pd.Series({"mtype": "L23_MC"})
    result = conn_prob(
        pre_synaptic_cell_group=pre_synaptic_cell_type,
        post_synaptic_cell_group=post_synaptic_cell_type)
    assert isinstance(result, (np.float, float)), type(result)
    assert np.isnan(result) or result < 1, result

def test_get_summary_with_series_input():
    """
    `PathwayProperty.get_summary(...)` should return a pandas.Series
    when the input is
        pre_synaptic_cell_group: pandas.Series
        post_synaptic_cell_group: pandas.Series
    And should cache the results if specified in it's initialization
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cell_type =\
        pd.Series({"mtype": "L23_MC"})
    post_synaptic_cell_type =\
        pd.Series({"mtype": "L23_MC"})
    result = conn_prob.get_summary(
        pre_synaptic_cell_group=pre_synaptic_cell_type,
        post_synaptic_cell_group=post_synaptic_cell_type)
    assert isinstance(result, pd.Series), result
    if result.pairs_total == 0:
        assert result.pairs_connected == 0,\
            result.pairs_connected
        assert np.isnan(result.connection_probability),\
            result.connection_probability
    else:
        expected = result.pairs_connected / result.pairs_total
        assert result.connection_probability == expected,\
            result

def test_call_with_pathway_input():
    """
    `PathwayProperty`.__call__(...) should return a float
    when the query input is a pathway.
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pathway = CellType.pathway(
        pd.Series({"mtype": "L23_MC"}),
        pd.Series({"mtype": "L23_MC"}))
    result = conn_prob(pathway)
    assert isinstance(result, (np.float, float)), type(result)
    assert np.isnan(result) or result < 1, result


def test_call_with_array_input():
    """
   `PathwayProperty.get_summary(...)` should return a pandas.Series
    when the input is
        `pre_synaptic_cell_group` : `numpy.ndarray`
        `post_synaptic_cell_group`: `numpy.ndarray`
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        circuit_model.cells.sample(n=100).gid.values
    post_synaptic_cells =\
        circuit_model.cells.sample(n=100).gid.values

    result = conn_prob(
        pre_synaptic_cell_group=pre_synaptic_cells,
        post_synaptic_cell_group=post_synaptic_cells)

    assert isinstance(result, (np.float, float))
    assert result < 1.

def test_get_summary_with_array_input():
    """
   `PathwayProperty.get_summary(...)` should return a pandas.Series
    when the input is
        `pre_synaptic_cell_group` : `pandas.DataFrame`
        `post_synaptic_cell_group`: `pandas.DataFrame`
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        circuit_model.cells.sample(n=100).gid.values
    post_synaptic_cells =\
        circuit_model.cells.sample(n=100).gid.values
    result = conn_prob.get_summary(
        pre_synaptic_cells,
        post_synaptic_cells)
    assert isinstance(result, pd.Series), result
    assert result.pairs_total == 10000, result
    assert result.pairs_connected < 10000, result
    assert result.connection_probability < 1., result

def test_call_with_dataframes_and_groupby():
    """
    `PathwayProperty.__call__` should return a float
    when the query input is
        pre_synaptic_cell_group : pandas.DataFrame
        post_synaptic_cell_group: pandas.DataFrame
        groupby : GroupVariables that are not None
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    post_synaptic_cells =\
        circuit_model.cells.sample(n=100)
    result = conn_prob(
        pre_synaptic_cell_group=pre_synaptic_cells,
        post_synaptic_cell_group=post_synaptic_cells,
        groupby=GroupByVariables(
            pre_synaptic_cell_type_specifier={"mtype",},
            post_synaptic_cell_type_specifier={"mtype",}))

    assert isinstance(result, pd.DataFrame)
    assert "pre_synaptic_mtype" in result.index.names
    assert "post_synaptic_mtype" in result.index.names
    assert ("pairs_total") in result.columns
    assert ("pairs_connected") in result.columns
    assert ("connection_probability") in result.columns
