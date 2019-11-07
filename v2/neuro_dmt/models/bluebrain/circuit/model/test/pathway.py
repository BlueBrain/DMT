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
from neuro_dmt.models.bluebrain.circuit.model.pathway import\
    Pathway

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


def test_pathway_property_dataframes_input():
    """
    `PathwayProperty` instance should return a pandas.Series when the input is
    pandas.DataFrames for `pre_synaptic_cell_group` and `post_synaptic_cell_group`
    and no `groupby` are not provided in the arguments.
    """
    circuit_model =\
        TestCircuit.mock_circuit_model
    conn_prob =\
        circuit_model.connection_probability
    pre_synaptic_cells =\
        Pathway.as_pre_synaptic(
            circuit_model.cells.sample(n=100))
    post_synaptic_cells =\
        Pathway.as_post_synaptic(
            circuit_model.cells.sample(n=100))
    result = conn_prob(
        pre_synaptic_cell_group=pre_synaptic_cells,
        post_synaptic_cell_group=post_synaptic_cells)

    assert isinstance(result, pd.Series), result
    assert result.pairs.total == 10000, result
    assert result.pairs.connected < 10000, result
    assert result.pairs.connection_probability < 1., result



