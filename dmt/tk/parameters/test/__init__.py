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
Test develop the behavior of `class Parameters`
"""
from collections import Mapping
import pytest as pyt
import pandas as pd
from .. import Parameters

def test_parameters_from_dataframe():
    """
    `class Parameters` should work with a pandas dataframe.
    """
    parameters = Parameters(
        pd.DataFrame({"layer": range(1,7 )}))
    assert parameters.variables == ["layer"]
    assert isinstance(parameters._resolve_values(), pd.DataFrame)
    sampling_params = parameters.for_sampling(size=20)
    assert len(sampling_params) == 120, sampling_params
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

    index = parameters.get_index(sampling_params)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

def test_parameters_from_callable_returning_dataframe():
    """
    `class Parameters` should work with with a callable
    that returns a dataframe
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1,7 )}))

    with pyt.raises(TypeError):
        parameters.variables

    parameters = parameters.for_model(None, None)

    assert parameters.variables == ["layer"]

    sampling_params = parameters.for_sampling(size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())
        
    index = parameters.get_index(sampling_params)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

def test_parameters_from_callable_returning_iterable():
    """
    `class Parameters` should work with a callable
    that returns an iterable of mappings of parameter labels to values.
    """

    parameters = Parameters(
        lambda adapter, model: ({"layer": layer} for layer in range(1,7)))

    with pyt.raises(TypeError):
        parameters.variables

    parameters = parameters.for_model(None, None)

    assert parameters.variables == ["layer"]

    sampling_params = parameters.for_sampling(size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

    index = parameters.get_index(sampling_params)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

def test_parameters_from_callable_with_labels():
    """
    `class Parameters` can be initialized with a pandas DataFrame and labels.
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1,7 )}),
        labels=("layer",))

    assert parameters.variables == ["layer"]

    sampling_params = parameters.for_sampling(None, None, size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

    index = parameters.get_index(sampling_params)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

def test_parameters_from_callable_returning_dataframe_for_sampling():
    """
    Calling parameters.for_sampling should set `Parameters` instance's labels.
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1, 7)}))

    with pyt.raises(TypeError):
        parameters.variables

    sampling_params = parameters.for_sampling(None, None, size=20)
    assert parameters.variables == ["layer"]
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

    for row in sampling_params:
        assert isinstance(row, Mapping), "{} is not a Mapping".format(type(row))
        assert len(row) == 1
        assert "layer" in row.keys()

    index = parameters.get_index(sampling_params)
    assert len(index) == 120, sampling_params
    assert isinstance(index, pd.Index)

    sampling_params = parameters.for_sampling(None, None, size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

def test_parameters_from_callable_returning_iterable_for_sampling():
    """
    Calling parameters.for_sampling should set `Parameters` instance's labels.
    """
    parameters = Parameters(
        lambda adapter, model: ({"layer": layer} for layer in range(1,7)))

    with pyt.raises(TypeError):
        parameters.variables

    sampling_params = parameters.for_sampling(None, None, size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

    assert sampling_params, str(sampling_params)

    assert parameters.variables == ["layer"]

    index = parameters.get_index(sampling_params)
    assert len(index) == 120, len(index)
    assert isinstance(index, pd.Index)

    sampling_params = parameters.for_sampling(None, None, size=20)
    assert len(sampling_params) == 120
    assert all(
        count == 20
        for count in pd.DataFrame(sampling_params)["layer"].value_counts())

def test_parametere_from_callable_returning_iterable_containing_unaligned_dicts():
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
