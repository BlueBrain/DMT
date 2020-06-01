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
Test develop assets that we will use to test develop documented analyses.
"""
import pandas as pd
from .import MockCircuitAdapter, MockCircuitModel

def test_adapter_model():
    circuit_model = MockCircuitModel()
    adapter = MockCircuitAdapter()

    thicknesses = adapter.get_layer_thickness_values(
        circuit_model, sample_size=20, region="mc0_Column")

    assert isinstance(thicknesses, pd.DataFrame), thicknesses

    assert thicknesses.shape == (20, 6), thicknesses.shape

    for layer in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        assert layer in thicknesses.columns
