# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop `Data`.
"""

from .import *

def test_data_empty():
    """
    Empty `Data` object should not save anything....
    """
    adapter = MockAdapter()
    model = MockModel()

    data = Data()
    value = data(adapter, model)
    assert value is None
    path_test = path_save.joinpath("empty")
    data.save(value, path_save)

    path_data = path_test.joinpath("data")
    assert not os.path.exists(path_data)

def test_data_single_dataframe():
    """
    A `Data` instance can be created with a single dataframe.
    """
    adapter = MockAdapter()
    model = MockModel()

    data = Data(measurement=mock_cell_density)
    value_data = data(adapter, model)

    assert isinstance(value_data, pd.DataFrame), type(value_data)
    assert "layer" in value_data.columns
    assert "cell_density" in value_data.columns

    data.save(value_data, path_save)
    assert os.path.isfile(path_save.joinpath("data.csv"))
    return True

def test_data_multiple_dataframes():

    adapter = MockAdapter()
    model = MockModel()

    measurement ={
        "cell_density": mock_cell_density(),
        "inhibitory_fraction": mock_inh_fraction()}
    data = Data(measurement=measurement)
    value_data = data(adapter, model)
    assert isinstance(value_data, Mapping)

    cell_density = value_data["cell_density"]
    assert isinstance(cell_density, pd.DataFrame),\
        type(cell_density)
    assert "layer" in cell_density.columns
    assert "cell_density" in cell_density.columns

    inhibitory_fraction = value_data["inhibitory_fraction"]
    assert isinstance(inhibitory_fraction, pd.DataFrame),\
        type(inhibitory_fraction)
    assert "layer" in inhibitory_fraction.columns,\
        inhibitory_fraction.columns
    assert "inhibitory_fraction" in inhibitory_fraction.columns,\
        inhibitory_fraction.columns

    data.save(value_data, path_save)
    path_data = path_save.joinpath("data")
    assert os.path.isfile(path_data.joinpath("cell_density.csv"))
    assert os.path.isfile(path_data.joinpath("inhibitory_fraction.csv"))
    return True


def test_data_multiple_callables():

    adapter = MockAdapter()
    model = MockModel()

    measurement ={
        "cell_density": mock_cell_density,
        "inhibitory_fraction": mock_inh_fraction}
    data = Data(measurement=measurement)
    value_data = data(adapter, model)
    assert isinstance(value_data, Mapping)

    cell_density = value_data["cell_density"]
    assert isinstance(cell_density, pd.DataFrame),\
        type(cell_density)
    assert "layer" in cell_density.columns
    assert "cell_density" in cell_density.columns

    inhibitory_fraction = value_data["inhibitory_fraction"]
    assert isinstance(inhibitory_fraction, pd.DataFrame),\
        type(inhibitory_fraction)
    assert "layer" in inhibitory_fraction.columns,\
        inhibitory_fraction.columns
    assert "inhibitory_fraction" in inhibitory_fraction.columns,\
        inhibitory_fraction.columns

    data.save(value_data, path_save)
    path_data = path_save.joinpath("data")
    assert os.path.isfile(path_data.joinpath("cell_density.csv"))
    assert os.path.isfile(path_data.joinpath("inhibitory_fraction.csv"))
    return True
