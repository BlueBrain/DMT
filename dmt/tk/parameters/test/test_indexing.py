"""
Test develop the indexing behavior of `class Parameters`
"""
from collections import Mapping
import pytest as pyt
import pandas as pd
from .. import Parameters

def test_parameters_from_callable_returning_iterable():
    """
    `class Parameters` should work with a callable
    that returns an iterable of mappings of parameter labels to values.
    """
    parameters = Parameters(
        lambda adapter, model: [
            {"layer": 1},
            {"layer": 1, "region": "R"},
            {"region": "S"},
            {}])

    with pyt.raises(TypeError):
        parameters.variables

    sampling_params = parameters.for_sampling(None, None, size=20)
    with pyt.raises(TypeError):
        parameters.variables
    assert len(sampling_params) == 80

    index = parameters.get_index(sampling_params)
    assert len(index) == 80
    assert isinstance(index, pd.Index)

    parameters = parameters.for_model(None, None)

    assert "layer" in parameters.variables, parameters.variables
    assert "region" in parameters.variables, parameters.variables

    sampling_params = parameters.for_sampling(size=20)
    assert len(sampling_params) == 80

    index = parameters.get_index(sampling_params)
    assert len(index) == 80
    assert isinstance(index, pd.Index)

    assert "region" in index.names
    assert "layer" in index.names
    assert "blah" not in index.names

def test_parameters_from_callable_returning_iterable_mapping_to_dicts():
    """
    `class Parameters` should work with a callable
    that returns an iterable of mappings of parameter labels to values
    that are dicts
    """
    parameter_list = [
        {
            "pre": {"layer": 1, "mtype": "L1_BC", "sclass": "INT"},
            "post": {"layer": 5, "mtype": "L5_BC", "sclass": "INT"}
        },
        {
            "pre": {"layer": 2, "mtype": "L23_PC", "sclass": "EXC"},
            "post": {"layer": 3, "mtype": "L23_PC", "sclass": "EXC"}
        },
        {
            "pre": {"layer": 5, "mtype": "L5_UPC", "sclass": "EXC"},
            "post": {"layer": 6, "mtype": "L6_UPC", "sclass": "EXC"}
        }]
    parameters =\
        Parameters(
            lambda adapter, model: parameter_list,
            with_labels=False)

    with pyt.raises(TypeError):
        parameters.variables
    
    size = 20
    sampling_params = parameters.for_sampling(None, None, size=size)
    with pyt.raises(TypeError):
        parameters.variables
    for row in parameter_list:
        assert sampling_params.count(row) == size, row

    index = parameters.get_index(sampling_params)
    assert len(index) == size * len(parameter_list)
    assert isinstance(index, pd.MultiIndex)

    parameters = parameters.for_model(None, None)

    assert "pre" in parameters.variables, parameters.variables
    assert "post" in parameters.variables, parameters.variables

    sampling_params = parameters.for_sampling(size=20)
    assert len(sampling_params) == size * len(parameter_list)

    sampling_dataframe = parameters.as_dataframe(sampling_params)
    assert ("pre", "layer") in list(sampling_dataframe.columns.values)
    assert ("post", "layer") in list(sampling_dataframe.columns.values)
    
    index = parameters.get_index(sampling_params)
    assert len(index) == size * len(parameter_list)
    assert isinstance(index, pd.MultiIndex)

    assert ("pre", "layer") in index.names
    for row in parameter_list:
        pre_layer_values = list(index.get_level_values(("pre", "layer")))
        assert pre_layer_values.count(row["pre"]["layer"]) == size
        post_layer_values = list(index.get_level_values(("post", "layer")))
        assert  post_layer_values.count(row["post"]["layer"]) == size
        
    assert ("post", "layer") in index.names
