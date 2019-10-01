"""
Test develop the behavior of `class Parameters`
"""
import pytest as pyt
import pandas as pd
from .. import Parameters

def test_parameters_from_dataframe():
    """
    `class Parameters` can be initialized with a pandas dataframe.
    """
    parameters = Parameters(
        pd.DataFrame({"layer": range(1,7 )}))
    assert parameters.variables == ["layer"]
    index = parameters.index(sample_size=20)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

    sampling_params =\
        pd.DataFrame(list(parameters.for_sampling(size=10)))
    assert sampling_params.shape[0] == 60
    assert all(count == 10 for count in sampling_params["layer"].value_counts())

def test_parameters_from_callable():
    """
    `class Parameters` can be initialized with a pandas dataframe.
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1,7 )}))

    with pyt.raises(TypeError):
        parameters.variables

    parameters = parameters.for_model(None, None)

    assert parameters.variables == ["layer"]

    index = parameters.index(sample_size=20)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

    sampling_params =\
        pd.DataFrame(list(parameters.for_sampling(size=10)))
    assert sampling_params.shape[0] == 60
    assert all(count == 10 for count in sampling_params["layer"].value_counts())

def test_parameters_from_callable_with_labels():
    """
    `class Parameters` can be initialized with a pandas DataFrame and labels.
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1,7 )}),
        labels=("layer",))

    assert parameters.variables == ["layer"]

    index = parameters.index(None, None, sample_size=20)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

    sampling_params =\
        pd.DataFrame(list(parameters.for_sampling(None, None, size=10)))
    assert sampling_params.shape[0] == 60
    assert all(count == 10 for count in sampling_params["layer"].value_counts())


def test_parameters_from_callable_for_sampling():
    """
    Calling parameters.for_sampling should set labels.
    """
    parameters = Parameters(
        lambda adapter, model: pd.DataFrame({"layer": range(1,7 )}))

    with pyt.raises(TypeError):
        parameters.variables

    sampling_params =\
        pd.DataFrame(list(parameters.for_sampling(None, None, size=10)))

    assert parameters.variables == ["layer"]

    index = parameters.index(None, None, sample_size=20)
    assert len(index) == 120
    assert isinstance(index, pd.Index)

    sampling_params =\
        pd.DataFrame(list(parameters.for_sampling(None, None, size=10)))
    assert sampling_params.shape[0] == 60
    assert all(count == 10 for count in sampling_params["layer"].value_counts())
